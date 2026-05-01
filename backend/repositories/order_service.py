import uuid
from sqlalchemy.orm import Session
from .order_repository import OrderRepository
from ..models import Pedido, HardwareCommand

class OrderService:
    def __init__(self, db: Session):
        self.repo = OrderRepository(db)
        self.db = db

    def process_checkout(self, order_id: str, payment_method: str) -> Pedido:
        """
        Lógica profesional de cobro:
        1. Actualizar estado del pedido.
        2. Abrir cajón si es efectivo (a través de HardwareCommand en BBDD).
        """
        order = self.repo.update_status(order_id, "EN_PREPARACION")
        if not order:
            raise Exception("Pedido no encontrado")
        
        order.metodo_pago = payment_method
        
        if payment_method == "EFECTIVO":
            nuevo_cmd = HardwareCommand(
                id=str(uuid.uuid4()),
                accion="abrir_caja",
                origen="backend_enterprise"
            )
            self.db.add(nuevo_cmd)
            
        self.db.commit()
        return order

    def get_dashboard_summary(self):
        orders = self.repo.get_today_orders()
        total_sales = sum(o.total for o in orders)
        return {
            "total_sales": total_sales,
            "order_count": len(orders),
            "avg_ticket": total_sales / len(orders) if orders else 0
        }
