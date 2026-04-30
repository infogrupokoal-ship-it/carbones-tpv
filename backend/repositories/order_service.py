from sqlalchemy.orm import Session
from .order_repository import OrderRepository
from ..models import Pedido
from ..routers.hardware import trigger_drawer_open # Reutilizando lógica existente

class OrderService:
    def __init__(self, db: Session):
        self.repo = OrderRepository(db)
        self.db = db

    def process_checkout(self, order_id: str, payment_method: str) -> Pedido:
        """
        Lógica profesional de cobro:
        1. Actualizar estado del pedido.
        2. Abrir cajón si es efectivo.
        3. (Futuro) Notificar a la nube.
        """
        order = self.repo.update_status(order_id, "EN_PREPARACION")
        if not order:
            raise Exception("Pedido no encontrado")
        
        order.metodo_pago = payment_method
        self.db.commit()

        if payment_method == "EFECTIVO":
            trigger_drawer_open()
            
        return order

    def get_dashboard_summary(self):
        orders = self.repo.get_today_orders()
        total_sales = sum(o.total for o in orders)
        return {
            "total_sales": total_sales,
            "order_count": len(orders),
            "avg_ticket": total_sales / len(orders) if orders else 0
        }
