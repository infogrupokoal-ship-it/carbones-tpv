import logging
import os
from typing import Optional

import stripe

logger = logging.getLogger("StripeService")


class StripeGateway:
    """Servicio profesional para la gestión de pagos con Stripe."""

    def __init__(self):
        stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
        self.webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    async def crear_checkout_session(
        self, pedido_id: str, total: float, email_cliente: Optional[str] = None
    ):
        """Crea una sesión de pago para el cliente."""
        try:
            # Convertir a céntimos
            amount = int(total * 100)

            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": "eur",
                            "product_data": {
                                "name": f"Pedido Carbones y Pollos #{pedido_id}",
                            },
                            "unit_amount": amount,
                        },
                        "quantity": 1,
                    }
                ],
                mode="payment",
                success_url=os.getenv("BASE_URL") + "/pago_exitoso?id=" + pedido_id,
                cancel_url=os.getenv("BASE_URL") + "/pago_cancelado?id=" + pedido_id,
                customer_email=email_cliente,
                metadata={"pedido_id": pedido_id},
            )
            return session.url
        except Exception as e:
            logger.error(f"Error Stripe Session: {e}")
            return None

    def validar_webhook(self, payload: str, sig_header: str):
        """Verifica la autenticidad de las notificaciones de Stripe."""
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, self.webhook_secret
            )
            return event
        except Exception as e:
            logger.error(f"Webhook Signature Error: {e}")
            return None
