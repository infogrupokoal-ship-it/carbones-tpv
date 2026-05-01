import stripe
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Pedido, Producto, Notificacion
from ..config import settings
from ..utils.logger import logger
from typing import Optional
import requests

router = APIRouter(prefix="/payments", tags=["Pagos"])

if settings.STRIPE_SECRET_KEY:
    stripe.api_key = settings.STRIPE_SECRET_KEY

@router.post("/stripe/create-session/{pedido_id}")
async def create_checkout_session(pedido_id: str, db: Session = Depends(get_db)):
    """Crea una sesión de pago en Stripe para un pedido específico."""
    pedido = db.query(Pedido).get(pedido_id)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    if not settings.STRIPE_SECRET_KEY:
        raise HTTPException(status_code=500, detail="Stripe no configurado en el servidor")

    try:
        line_items = []
        for item in pedido.items:
            prod = db.query(Producto).get(item.producto_id)
            line_items.append({
                'price_data': {
                    'currency': 'eur',
                    'product_data': {
                        'name': prod.nombre if prod else "Producto",
                        'description': prod.descripcion if prod else "",
                    },
                    'unit_amount': int(item.precio_unitario * 100),
                },
                'quantity': item.cantidad,
            })

        if pedido.metodo_envio == "DOMICILIO":
            line_items.append({
                'price_data': {
                    'currency': 'eur',
                    'product_data': { 'name': 'Servicio de Entrega a Domicilio' },
                    'unit_amount': 250, 
                },
                'quantity': 1,
            })

        # Base URL dinámica para entornos (Local vs Render)
        base_url = "https://carbones-tpv.onrender.com" if not settings.DEBUG else "http://localhost:8000"

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=f"{base_url}/static/kiosko.html?status=success&order_id={pedido_id}",
            cancel_url=f"{base_url}/static/kiosko.html?status=cancelled",
            client_reference_id=pedido_id,
            customer_email=pedido.cliente.email if (pedido.cliente and pedido.cliente.email) else None,
            metadata={
                "pedido_id": pedido_id,
                "numero_ticket": pedido.numero_ticket,
                "cliente_nombre": pedido.cliente.nombre if pedido.cliente else "Anónimo",
                "envio": pedido.metodo_envio
            }
        )

        pedido.stripe_session_id = checkout_session.id
        db.commit()

        return {"url": checkout_session.url, "session_id": checkout_session.id}
    except Exception as e:
        logger.error(f"STRIPE_ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al procesar la pasarela de pago")

@router.post("/whatsapp-link/{pedido_id}")
async def send_payment_link_whatsapp(pedido_id: str, telefono: str, db: Session = Depends(get_db)):
    """Genera un enlace de pago y lo envía por WhatsApp al cliente."""
    pedido = db.query(Pedido).get(pedido_id)
    if not pedido: raise HTTPException(404, "Pedido inexistente")
    
    # Generar sesión de Stripe primero
    session_data = await create_checkout_session(pedido_id, db)
    payment_url = session_data["url"]
    
    msg = (
        f"🔥 *CARBONES Y POLLOS*\n\n"
        f"Hola! Tu pedido *{pedido.numero_ticket}* está listo para ser procesado.\n"
        f"Total a pagar: *{pedido.total}€*\n\n"
        f"Puedes realizar el pago seguro aquí:\n{payment_url}\n\n"
        f"¡Gracias por elegirnos!"
    )
    
    # Enviar vía WAHA
    try:
        waha_payload = {
            "chatId": f"{telefono}@c.us",
            "text": msg,
            "session": "default"
        }
        requests.post(f"{settings.WAHA_URL}/api/sendText", json=waha_payload, timeout=5)
        
        # Registrar notificación
        notif = Notificacion(
            tipo="WHATSAPP",
            destino=telefono,
            asunto="Link de Pago",
            mensaje=msg,
            estado="ENVIADO"
        )
        db.add(notif)
        db.commit()
        
        return {"status": "sent", "url": payment_url}
    except Exception as e:
        logger.error(f"WAHA_PAYMENT_LINK_ERROR: {str(e)}")
        return {"status": "error", "message": "No se pudo enviar el WhatsApp, pero el link es válido", "url": payment_url}

@router.post("/stripe/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Confirmación industrial de pagos vía Webhook con validación de firma."""
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        if endpoint_secret and sig_header:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        else:
            # Fallback para desarrollo sin secreto configurado
            event = await request.json()
            logger.warning("⚠️ WEBHOOK_SECURITY: Procesando evento sin validación de firma (STRIPE_WEBHOOK_SECRET no configurado).")
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"❌ WEBHOOK_AUTH_FAILED: Firma de Stripe inválida.")
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        pedido_id = session.get('client_reference_id')
        
        if pedido_id:
            pedido = db.query(Pedido).get(pedido_id)
            if pedido:
                # Transacción atómica para marcar como pagado
                pedido.estado = "PAGADO"
                pedido.stripe_payment_status = "paid"
                pedido.external_payment_id = session.get('payment_intent')
                
                # Registrar en auditoría
                from ..models import AuditLog
                audit = AuditLog(
                    usuario_id=None, # Pago externo
                    accion="PAGO_STRIPE_COMPLETADO",
                    entidad="PEDIDO",
                    entidad_id=pedido_id,
                    detalles=f"Pago confirmado vía Stripe. Intent: {pedido.external_payment_id}",
                    ip_origen=request.client.host
                )
                db.add(audit)
                db.commit()
                
                logger.info(f"💰 PAGO CONFIRMADO: Pedido {pedido.numero_ticket} liquidado.")
                
                # Disparar notificaciones post-pago
                # Enviar ticket por WhatsApp si tenemos el teléfono
                if pedido.cliente and pedido.cliente.telefono:
                    # Logic to send confirmation via notification service
                    pass

    return {"status": "success"}
