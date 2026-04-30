import logging
from sqlalchemy.orm import Session
from .ai_agent import ask_asador_ai
from .models import MovimientoStock, Producto, LogOperativo
from .database import SessionLocal
import uuid
import json

logger = logging.getLogger("WhatsAppAIBridge")

class WhatsAppAIBridge:
    @staticmethod
    async def process_incoming_message(message_text: str, sender_id: str):
        """
        Procesa mensajes de voz/texto enviados por el equipo vía WhatsApp.
        Convierte lenguaje natural en acciones de base de datos.
        """
        logger.info(f"Procesando mensaje de {sender_id}: {message_text}")
        
        # 1. Consultar a la IA para interpretar la intención
        prompt = f"""
        Interpreta este mensaje de un empleado del asador: "{message_text}"
        
        Posibles acciones:
        - PRODUCCION: Registrar que se han asado pollos.
        - MERMA: Registrar desperdicio.
        - STATUS: Preguntar por el estado del stock.
        
        Responde ÚNICAMENTE en formato JSON:
        {{
            "accion": "PRODUCCION|MERMA|STATUS|UNKNOWN",
            "producto": "nombre_producto",
            "cantidad": n,
            "respuesta_texto": "Mensaje de confirmación para el empleado"
        }}
        """
        
        try:
            ai_response_raw = await ask_asador_ai(prompt, user_role="staff")
            # Limpiar posibles bloques de código markdown
            ai_response_raw = ai_response_raw.replace("```json", "").replace("```", "").strip()
            data = json.loads(ai_response_raw)
            
            if data["accion"] == "UNKNOWN":
                return "Koal-AI: No he entendido bien. Prueba con 'He asado 20 pollos' o 'Hay 5 ensaladas de merma'."
            
            # 2. Ejecutar Acción en DB
            db = SessionLocal()
            try:
                if data["accion"] in ["PRODUCCION", "MERMA"]:
                    # Buscar producto similar
                    prod = db.query(Producto).filter(Producto.nombre.contains(data["producto"])).first()
                    if prod:
                        cant = data["cantidad"] if data["accion"] == "PRODUCCION" else -data["cantidad"]
                        mov = MovimientoStock(
                            id=str(uuid.uuid4()),
                            producto_id=prod.id,
                            cantidad=cant,
                            tipo=data["accion"],
                            descripcion=f"Registrado vía WhatsApp AI por {sender_id}"
                        )
                        prod.stock_actual += cant
                        db.add(mov)
                        
                        # Log operativo
                        db.add(LogOperativo(
                            modulo="AI_BRIDGE",
                            nivel="INFO",
                            mensaje=f"Acción {data['accion']} ejecutada para {prod.nombre}"
                        ))
                        db.commit()
                        return f"✅ Entendido. He registrado {abs(cant)} {prod.nombre} como {data['accion'].lower()}."
                    else:
                        return f"❌ No encuentro el producto '{data['producto']}' en el sistema."
                
                elif data["accion"] == "STATUS":
                    # El agente ya inyecta contexto, así que la respuesta de la IA suele ser suficiente
                    return data["respuesta_texto"]
                    
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error en AI Bridge: {e}")
            return "⚠️ Koal-AI: Error interno al procesar tu solicitud."

        return "Mensaje procesado."
