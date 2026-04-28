import os
from dotenv import load_dotenv
import google.generativeai as genai
from sqlalchemy.orm import Session
from models import Producto, Cliente

load_dotenv()
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY", "YOUR_GEMINI_KEY"))
model_name = "models/gemini-2.0-flash" 

def _preparar_catalogo(db: Session):
    productos = db.query(Producto).filter(Producto.is_active == True).all()
    catalogo_text = "\n".join([f"- ID: {p.id} | Nombre: {p.nombre} | Precio: {p.precio}€ | Stock: {p.stock_actual}" for p in productos])
    return catalogo_text

def procesar_mensaje_whatsapp(db: Session, sender_phone: str, mensaje: str, responsables: list):
    catalogo_text = _preparar_catalogo(db)
    is_admin = sender_phone in responsables
    
    # Tool definitions tightly bound to the DB Session
    def tool_registrar_pedido_kiosko(items: list, origen: str = "WHATSAPP"):
        """Registra un pedido de comida."""
        import ai_tools
        return ai_tools.registrar_pedido_kiosko(db, cliente.id, items, origen)

    def tool_actualizar_stock_cocina(producto_id: int, cantidad_anadida: int, precio_nuevo: float = None, alergenos: str = None):
        """Añade inventario producido recientemente."""
        import ai_tools
        return ai_tools.actualizar_stock_cocina(db, producto_id, cantidad_anadida, precio_nuevo, alergenos)

    cliente = None
    if not is_admin:
        cliente = db.query(Cliente).filter(Cliente.telefono == sender_phone).first()
        if not cliente:
            cliente = Cliente(telefono=sender_phone, nivel_fidelidad="BRONCE")
            db.add(cliente)
            db.commit()
            db.refresh(cliente)

    if is_admin:
         system_instruction = f"""
         Eres el sistema central de cocina de 'Carbones y Pollos'. 
         Hablas con un responsable o cocinero (+{sender_phone}).
         Tu catálogo actual es:\n{catalogo_text}
         TUS TAREAS:
         1. Si el cocinero te dice que ha hecho/producido comida, USA la funcion 'tool_actualizar_stock_cocina'. 
         Nunca inventes las respuestas de la BD, siempre ejecuta la tool de cocina.
         """
         tools_to_use = [tool_actualizar_stock_cocina]
    else:
         contexto_fidelidad = f"Nombre: {cliente.nombre or 'Desconocido'}. Nivel: {cliente.nivel_fidelidad}. Preferencias: {cliente.preferencias or 'Ninguna'}."
         system_instruction = f"""
         Eres el asistente y barman de 'Carbones y Pollos'.
         Hablas con un cliente (Tlf: {sender_phone}). {contexto_fidelidad}

         Tu catálogo actual es:\n{catalogo_text}
         TUS TAREAS:
         1. Atiende amablemente y recibe el pedido de comida. Entiende su lenguaje natural.
         2. Si dicen que confirman el pedido, USA la funcion 'tool_registrar_pedido_kiosko' enviando el array de productos (ID y cantidades).
         3. Recuerda: eres amable y ofreces ventas cruzadas.
         """
         tools_to_use = [tool_registrar_pedido_kiosko]

    try:
         model = genai.GenerativeModel(model_name, system_instruction=system_instruction, tools=tools_to_use)
         
         # Note: For multi-turn chats we would store chat history. For POC we spawn a one-shot chat.
         chat = model.start_chat(enable_automatic_function_calling=True)
         resp = chat.send_message(mensaje)
         
         if not is_admin and cliente:
             cliente.visitas += 1
             db.commit()
             
         return resp.text
    except Exception as e:
         return f"❌ Lo siento, ha ocurrido un error interno de inteligencia artificial. {str(e)}"
