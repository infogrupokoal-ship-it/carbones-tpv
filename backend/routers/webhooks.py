from fastapi import APIRouter, Request, BackgroundTasks
from ..whatsapp_ai_bridge import WhatsAppAIBridge
from ..utils.logger import logger
import requests
from ..config import settings

router = APIRouter(prefix="/webhooks/whatsapp", tags=["Webhooks"])

@router.post("/receive")
async def receive_whatsapp(request: Request, background_tasks: BackgroundTasks):
    """
    Webhook para recibir mensajes de WAHA (WhatsApp HTTP API).
    """
    try:
        data = await request.json()
        # WAHA envía el mensaje en data['payload']['body']
        payload = data.get("payload", {})
        message_text = payload.get("body")
        sender_id = payload.get("from")
        
        if not message_text or not sender_id:
            return {"status": "ignored"}

        # Procesar asíncronamente para no bloquear el webhook
        background_tasks.add_task(process_and_reply, message_text, sender_id)
        
        return {"status": "received"}
    except Exception as e:
        logger.error(f"Error en webhook WhatsApp: {e}")
        return {"status": "error", "detail": str(e)}

async def process_and_reply(text: str, sender: str):
    respuesta = await WhatsAppAIBridge.process_incoming_message(text, sender)
    
    # Enviar respuesta de vuelta vía WhatsApp
    try:
        url = f"{settings.WAHA_URL}/api/sendText"
        requests.post(url, json={
            "chatId": sender,
            "text": respuesta,
            "session": "default"
        }, timeout=10)
    except Exception as e:
        logger.error(f"Error enviando respuesta a WhatsApp: {e}")
