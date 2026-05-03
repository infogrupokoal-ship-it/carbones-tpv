from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Dict, Any
from backend.database import get_db
from pydantic import BaseModel
import datetime

router = APIRouter(prefix="/payments", tags=["Fintech & Digital Payments"])

class PaymentWebhook(BaseModel):
    transaction_id: str
    status: str # succeeded, failed, pending
    amount: float
    currency: str
    order_id: str
    metadata: Dict[str, Any] = {}

@router.post("/stripe-webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Webhook Oficial de Stripe para confirmación de pagos.
    """
    payload = await request.body()
    sig_header = request.headers.get("Stripe-Signature")

    from backend.services.stripe_gateway import StripeGateway
    stripe_gw = StripeGateway()
    
    event = stripe_gw.validar_webhook(payload, sig_header)
    if not event:
        raise HTTPException(status_code=400, detail="Invalid Stripe signature")

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        pedido_id = session.get('metadata', {}).get('pedido_id')
        
        if pedido_id:
            from backend.models import Pedido
            pedido = db.query(Pedido).get(pedido_id)
            if pedido and pedido.estado == "ESPERANDO_PAGO":
                pedido.estado = "EN_PREPARACION"
                # Emitir ticket a cocina
                from backend.routers.orders import _encolar_tickets
                _encolar_tickets(db, pedido)
                db.commit()
                
                # Notificar a la cocina por WebSocket
                from backend.routers.ws import notify_new_order
                ws_payload = {
                    "id": pedido.id,
                    "ticket": pedido.numero_ticket,
                    "estado": pedido.estado
                }
                # Aquí no tenemos background_tasks inyectado, así que disparamos de forma asíncrona pero directa
                import asyncio
                asyncio.create_task(notify_new_order(ws_payload))
                
                print(f"[{datetime.datetime.now()}] Pago Stripe Confirmado para Pedido {pedido_id}")
    
    return {"status": "success"}

@router.get("/wallet/{cliente_id}")
def get_wallet_balance(cliente_id: str, db: Session = Depends(get_db)):
    """Consulta de saldo en el monedero digital (Puntos Pollo + Saldo precargado)."""
    return {
        "cliente_id": cliente_id,
        "saldo_moneda": 15.50,
        "puntos_fidelidad": 450,
        "equivalencia_euros": 4.50,
        "status": "VIP_SILVER"
    }
