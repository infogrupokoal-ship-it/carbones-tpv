import stripe
import os
import logging
from sqlalchemy.orm import Session
from models import Pedido

# Stripe config
STRIPE_API_KEY = os.environ.get("STRIPE_API_KEY", "sk_test_123")
stripe.api_key = STRIPE_API_KEY

def generar_enlace_pago(pedido_id: int, total: float, items_resumen: str):
    """
    Genera un enlace de pago de Stripe Checkout para un pedido.
    Total está en euros. Stripe recibe el monto en céntimos.
    """
    try:
        if not STRIPE_API_KEY or STRIPE_API_KEY == "sk_test_123":
            logging.warning("Usando API_KEY de Stripe por defecto. El pago será de prueba.")
        
        domain_url = os.environ.get("DOMAIN_URL", "http://127.0.0.1:8000")
        
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'eur',
                    'product_data': {
                        'name': f'Pedido #{pedido_id}',
                        'description': items_resumen,
                    },
                    'unit_amount': int(total * 100), # En céntimos
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f"{domain_url}/api/b2c/webhook_success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{domain_url}/static/registro_cliente.html",
            metadata={
                'pedido_id': str(pedido_id)
            }
        )
        return session.url
    except Exception as e:
        logging.error(f"Error generando link de pago Stripe: {e}")
        return None
