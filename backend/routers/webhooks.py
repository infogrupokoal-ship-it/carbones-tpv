from fastapi import APIRouter, Request, BackgroundTasks, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..whatsapp_ai_bridge import WhatsAppAIBridge
from ..services.stripe_gateway import StripeGateway
from ..utils.logger import logger
import requests
from ..config import settings

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])

@router.post("/whatsapp/receive")
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

@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    stripe_signature: str = Header(None),
    db: Session = Depends(get_db)
):
    """
    Webhook para recibir eventos de Stripe (pagos completados).
    Industrializa la transición de estado del pedido a EN_PREPARACION de forma autónoma.
    """
    payload = await request.body()
    stripe_gw = StripeGateway()
    
    event = stripe_gw.validar_webhook(payload, stripe_signature)
    if not event:
        logger.warning("Fallo validando la firma del webhook de Stripe.")
        raise HTTPException(status_code=400, detail="Invalid Stripe signature")
        
    if event.type == 'checkout.session.completed':
        session = event.data.object
        pedido_id = session.metadata.get("pedido_id")
        
        if pedido_id:
            logger.info(f"💰 Stripe Webhook: Pago confirmado para pedido {pedido_id}")
            try:
                from .orders import actualizar_estado
                actualizar_estado(pedido_id, "EN_PREPARACION", background_tasks, db)
                logger.info(f"Pedido {pedido_id} transicionado a EN_PREPARACION exitosamente.")
            except Exception as e:
                logger.error(f"Error procesando el pedido post-pago: {e}")
                
    return {"status": "success"}
