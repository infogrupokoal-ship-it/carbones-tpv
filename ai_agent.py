import os
import json
import logging
from sqlalchemy.orm import Session
from datetime import datetime
import google.generativeai as genai

from models import Producto, MovimientoStock, Pedido, ItemPedido

# Configurar Gemini
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    
def get_menu_text(db: Session, turno: str):
    """Devuelve un string con el menú disponible para el turno actual."""
    if turno == "manana":
        prods = db.query(Producto).filter(Producto.is_active == True, Producto.disponible_manana == True).all()
    else:
        prods = db.query(Producto).filter(Producto.is_active == True, Producto.disponible_tarde == True).all()
        
    menu = "Menú disponible:\n"
    for p in prods:
        menu += f"- {p.nombre} ({p.precio}€)\n"
    return menu

def procesar_mensaje_whatsapp(mensaje: str, from_number: str, db: Session) -> str:
    """
    Recibe un mensaje de WhatsApp, determina si es un empleado o un cliente,
    y ejecuta la acción correspondiente.
    """
    if not GEMINI_API_KEY:
        logging.error("GEMINI_API_KEY no configurada. El bot no puede responder.")
        return "Disculpa, el sistema automático está inactivo en este momento."

    # 1. Determinar el contexto (Turno actual)
    hora = datetime.now().hour
    turno = "manana" if hora < 16 else "noche"
    menu_actual = get_menu_text(db, turno)

    # 2. Instrucciones para la IA (System Prompt)
    system_prompt = f"""
Eres el asistente virtual omnicanal de 'Carbones y Pollos'. 
Recibes mensajes por WhatsApp. Tienes dos funciones principales:
1. ATENDER A EMPLEADOS/COCINEROS: Si el usuario dice que "ha sacado", "preparado", "hemos hecho" X cantidad de raciones o género, debes interpretar que es un reporte de inventario.
2. ATENDER A CLIENTES: Si el usuario quiere comprar comida (domicilio o recoger), debes tomarle nota basándote ÚNICAMENTE en este menú:
{menu_actual}

REGLAS DE RESPUESTA:
- Debes responder siempre en formato JSON para que el sistema lo procese.
- Si es empleado reportando género, formato:
  {{"intencion": "inventario", "accion": "sumar", "items": [{{"producto": "nombre_producto", "cantidad": 5}}], "respuesta_texto": "Mensaje para el cocinero confirmando"}}
- Si es cliente pidiendo, formato:
  {{"intencion": "pedido", "items": [{{"producto": "nombre_producto", "cantidad": 1}}], "tipo": "domicilio/recoger", "direccion": "si la ha dado", "respuesta_texto": "Mensaje natural para el cliente"}}
- Si es charla general o preguntas del menú, formato:
  {{"intencion": "chat", "respuesta_texto": "Mensaje para el cliente"}}

Intenta emparejar "nombre_producto" con algo del menú.
Si el usuario no dice cantidades o productos claros, pide aclaración en "respuesta_texto" pero deja "items" vacío.
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
        if intencion == "inventario":
            # Sumar stock reportado por el cocinero
            items = resultado.get("items", [])
            for item in items:
                nombre = item.get("producto", "").lower()
                cant = item.get("cantidad", 0)
                # Buscar producto (búsqueda aproximada básica)
                prod = db.query(Producto).filter(Producto.nombre.ilike(f"%{nombre}%")).first()
                if prod and cant > 0:
                    prod.stock_actual += cant
                    # Registrar movimiento
                    mov = MovimientoStock(
                        producto_id=prod.id,
                        cantidad=cant,
                        tipo="ENTRADA_PRODUCCION",
                        motivo="Reporte WhatsApp",
                        usuario_id=None # WhatsApp
                    )
                    db.add(mov)
            db.commit()
            
        elif intencion == "pedido":
            # Guardar pedido preliminar si hay items y es claro
            items = resultado.get("items", [])
            tipo_pedido = resultado.get("tipo", "recoger")
            direccion = resultado.get("direccion", "")
            
            if items:
                nuevo_pedido = Pedido(
                    origen="WHATSAPP",
                    estado="PENDIENTE",
                    total=0.0
                )
                db.add(nuevo_pedido)
                db.commit()
                db.refresh(nuevo_pedido)
                
                total = 0.0
                for item in items:
                    nombre = item.get("producto", "").lower()
                    cant = item.get("cantidad", 0)
                    prod = db.query(Producto).filter(Producto.nombre.ilike(f"%{nombre}%")).first()
                    
                    if prod and cant > 0:
                        ip = ItemPedido(
                            pedido_id=nuevo_pedido.id,
                            producto_id=prod.id,
                            cantidad=cant,
                            subtotal=prod.precio * cant
                        )
                        db.add(ip)
                        total += ip.subtotal
                
                nuevo_pedido.total = total
                # En un sistema real guardariamos direccion y tipo en el pedido,
                # para Fase 6 simplificamos usando las notas.
                nuevo_pedido.notas = f"Tipo: {tipo_pedido}. Dirección: {direccion}. Teléfono: {from_number}"
                db.commit()
                
                # Integrar Fase 7: Enlace de Stripe si es a domicilio o si prefiere pagar ya
                if tipo_pedido.lower() == "domicilio":
                    from stripe_service import generar_enlace_pago
                    resumen = ", ".join([f"{item.get('cantidad')}x {item.get('producto')}" for item in items])
                    url_pago = generar_enlace_pago(nuevo_pedido.id, total, resumen)
                    if url_pago:
                        respuesta_texto += f"\n\nPuedes pagar tu pedido de forma segura aquí: {url_pago}"
                    else:
                        respuesta_texto += f"\n\n(Aviso: El enlace de pago no se pudo generar. Pagarás al repartidor.)"

        return respuesta_texto
        
    except Exception as e:
        logging.error(f"Error procesando con Gemini: {e}")
        return "Lo siento, ha habido un error procesando tu mensaje."
