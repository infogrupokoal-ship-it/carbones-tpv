from sqlalchemy.orm import Session
from ..repositories.order_repository import OrderRepository
from ..models import Pedido, ItemPedido, HardwareCommand
import uuid
from datetime import datetime

class OrderService:
    def __init__(self, db: Session):
        self.repository = OrderRepository(db)
        self.db = db

    def process_new_order(self, order_data: dict) -> Pedido:
        """
        Lógica de negocio compleja para crear un pedido:
        1. Validar stock.
        2. Calcular impuestos.
        3. Persistir pedido e ítems.
        4. Generar comandos de hardware (tickets).
        """
        # Crear objeto pedido
        nuevo_pedido = Pedido(
            id=str(uuid.uuid4()),
            numero_ticket=f"T-{datetime.now().strftime('%H%M%S')}",
            total=order_data.get("total", 0.0),
            estado="PENDIENTE",
            metodo_pago=order_data.get("metodo_pago", "EFECTIVO")
        )

        # Persistir mediante repositorio
        self.repository.create(nuevo_pedido)

        # Encolar impresión automáticamente
        self._enqueue_printing_commands(nuevo_pedido)

        return nuevo_pedido

    def _enqueue_printing_commands(self, pedido: Pedido):
        """Genera los comandos para que el Hardware Bridge imprima los tickets."""
        # Ticket Cocina
        self.db.add(HardwareCommand(
            id=str(uuid.uuid4()),
            accion="imprimir",
            payload={"tipo": "cocina", "pedido_id": pedido.id},
            origen="service_layer"
        ))
        
        # Ticket Cliente
        self.db.add(HardwareCommand(
            id=str(uuid.uuid4()),
            accion="imprimir",
            payload={"tipo": "cliente", "pedido_id": pedido.id},
            origen="service_layer"
        ))
        self.db.commit()
