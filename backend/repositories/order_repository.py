from typing import List, Optional
from sqlalchemy.orm import Session
from ..models import Pedido
from sqlalchemy import func
from datetime import datetime

class OrderRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Pedido]:
        return self.db.query(Pedido).offset(skip).limit(limit).all()

    def get_by_id(self, order_id: str) -> Optional[Pedido]:
        return self.db.query(Pedido).filter(Pedido.id == order_id).first()

    def get_by_ticket(self, ticket_number: str) -> Optional[Pedido]:
        return self.db.query(Pedido).filter(Pedido.numero_ticket == ticket_number).first()

    def get_today_orders(self) -> List[Pedido]:
        today = datetime.now().date()
        return self.db.query(Pedido).filter(func.date(Pedido.fecha) == today).all()

    def create(self, order: Pedido) -> Pedido:
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        return order

    def update_status(self, order_id: str, status: str) -> Optional[Pedido]:
        order = self.get_by_id(order_id)
        if order:
            order.estado = status
            self.db.commit()
            self.db.refresh(order)
        return order
