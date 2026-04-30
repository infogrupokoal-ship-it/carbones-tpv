from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

class ItemPedidoBase(BaseModel):
    producto_id: str
    cantidad: int
    precio_unitario: float

class ItemPedidoCreate(ItemPedidoBase):
    pass

class ItemPedido(ItemPedidoBase):
    id: str
    pedido_id: str

    class Config:
        from_attributes = True

class PedidoBase(BaseModel):
    numero_ticket: Optional[str] = None
    estado: str = "PENDIENTE"
    metodo_pago: Optional[str] = None
    total: float = 0.0

class PedidoCreate(PedidoBase):
    items: List[ItemPedidoCreate]
    cliente_id: Optional[str] = None

class Pedido(PedidoBase):
    id: str
    fecha: datetime
    items: List[ItemPedido] = []

    class Config:
        from_attributes = True

class DashboardKPIs(BaseModel):
    total_ventas: float
    numero_pedidos: int
    ticket_medio: float
    ventas_efectivo: float
    ventas_tarjeta: float
