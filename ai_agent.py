import os
import json
import logging
import base64
from sqlalchemy.orm import Session
from datetime import datetime
import google.generativeai as genai

from models import Producto, MovimientoStock, Pedido, ItemPedido, Cliente

# Configurar Gemini
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    
def get_menu_text(db: Session, turno: str):
    """Devuelve un string con el menú disponible."""
    prods = db.query(Producto).filter(Producto.is_active == True).all()
    menu = "Menú disponible:\n"
    for p in prods:
        menu += f"- {p.nombre} ({p.precio}€)\n"
    return menu

def generate_magic_link(wa_id: str) -> str:
    # MVP: Simple base64 encoding of the wa_id. In production, use JWT.
    token = base64.b64encode(wa_id.encode('utf-8')).decode('utf-8')
    return f"http://127.0.0.1:8000/api/auth/magic_login?token={token}"

def procesar_mensaje_whatsapp(mensaje: str, from_number: str, db: Session) -> str:
    if not GEMINI_API_KEY:
        logging.error("GEMINI_API_KEY no configurada. El bot no puede responder.")
        return "Disculpa, el sistema automático está inactivo en este momento."

    # 1. Verificar o Crear Cliente (Omnicanalidad)
    cliente = db.query(Cliente).filter(Cliente.wa_id == from_number).first()
    is_new = False
    if not cliente:
        cliente = Cliente(
            wa_id=from_number,
            telefono=from_number,
            estado_registro="PENDIENTE_NOMBRE"
        )
        db.add(cliente)
        db.commit()
        db.refresh(cliente)
        is_new = True

    # 2. Instrucciones para la IA
    estado_cliente = "NUEVO (Pide su nombre)" if cliente.estado_registro == "PENDIENTE_NOMBRE" else f"REGISTRADO (Nombre: {cliente.nombre})"
    menu_actual = get_menu_text(db, "manana")

    system_prompt = f"""
Eres el asistente virtual omnicanal de 'Carbones y Pollos'. 
Recibes mensajes por WhatsApp del número {from_number}.
Estado del Cliente Actual: {estado_cliente}

Tus funciones:
1. ATENDER A EMPLEADOS/COCINEROS: Si el usuario reporta stock producido, formato:
   {{"intencion": "inventario", "accion": "sumar", "items": [{{"producto": "nombre_producto", "cantidad": 5}}], "respuesta_texto": "Mensaje confirmando"}}

2. GESTIONAR CLIENTES B2C:
   a) Si el cliente es NUEVO, amablemente pídele su nombre y guárdalo en la intención de registro:
      {{"intencion": "registro", "nombre_detectado": "Nombre", "respuesta_texto": "¡Hola Nombre! Aquí tienes tu acceso: [MAGIC_LINK]"}}
   b) Si el cliente quiere hacer un pedido, ver la carta, o ya es REGISTRADO, ofrécele el acceso a su portal B2C con el enlace mágico:
      {{"intencion": "magic_link", "respuesta_texto": "Aquí tienes tu acceso directo a la carta y pedidos: [MAGIC_LINK]"}}

REGLAS DE RESPUESTA:
- Responde SIEMPRE en JSON puro.
- Utiliza la etiqueta [MAGIC_LINK] en tu texto, yo la reemplazaré por la URL real.
- Intenta emparejar "nombre_producto" con este menú si te piden algo específico, pero prioriza mandarlos al MAGIC_LINK para que pidan por la web.
{menu_actual}
"""

    # 3. Llamar a Gemini
    try:
        model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=system_prompt)
        response = model.generate_content(
            mensaje,
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json",
            )
        )
        
        resultado = json.loads(response.text)
        intencion = resultado.get("intencion")
        respuesta_texto = resultado.get("respuesta_texto", "No he entendido bien, ¿puedes repetir?")
        
        # 4. Procesar la intención
        if intencion == "registro":
            nombre_detectado = resultado.get("nombre_detectado")
            if nombre_detectado:
                cliente.nombre = nombre_detectado
                cliente.estado_registro = "COMPLETADO"
                db.commit()
                
        if intencion == "inventario":
            items = resultado.get("items", [])
            for item in items:
                nombre = item.get("producto", "").lower()
                cant = item.get("cantidad", 0)
                prod = db.query(Producto).filter(Producto.nombre.ilike(f"%{nombre}%")).first()
                if prod and cant > 0:
                    prod.stock_actual += cant
                    db.add(MovimientoStock(producto_id=prod.id, cantidad=cant, tipo="ENTRADA_PRODUCCION"))
            db.commit()

        # Reemplazar MAGIC_LINK en el texto final
        if "[MAGIC_LINK]" in respuesta_texto:
            m_link = generate_magic_link(cliente.wa_id)
            respuesta_texto = respuesta_texto.replace("[MAGIC_LINK]", m_link)

        return respuesta_texto
        
    except Exception as e:
        logging.error(f"Error procesando con Gemini: {e}")
        return "Lo siento, ha habido un error procesando tu mensaje."
