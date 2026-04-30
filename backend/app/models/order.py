import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from ..core.database import Base

class Cliente(Base):
    __tablename__ = "clientes"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = Column(String(100), nullable=False)
    telefono = Column(String(20))
    puntos = Column(Integer, default=0)

class Pedido(Base):
    __tablename__ = "pedidos"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    numero_ticket = Column(String(50), unique=True)
    fecha = Column(DateTime, default=datetime.utcnow)
    total = Column(Float, nullable=False)
    base_imponible = Column(Float)
    iva_total = Column(Float)
    metodo_pago = Column(String(20)) # EFECTIVO, TARJETA, STRIPE
    estado = Column(String(20), default="PENDIENTE")
    cliente_id = Column(String(36), ForeignKey("clientes.id"), nullable=True)

    items = relationship("ItemPedido", back_populates="pedido")

class ItemPedido(Base):
    __tablename__ = "item_pedido"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    pedido_id = Column(String(36), ForeignKey("pedidos.id"))
    producto_id = Column(String(36))
    cantidad = Column(Integer, default=1)
    precio_unitario = Column(Float)
    
    pedido = relationship("Pedido", back_populates="items")
