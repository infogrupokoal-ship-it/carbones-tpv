import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import relationship
from ..core.database import Base

class Cliente(Base):
    __tablename__ = "clientes"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = Column(String, nullable=True)
    telefono = Column(String, unique=True, index=True)
    puntos = Column(Integer, default=0)
    pedidos = relationship("Pedido", back_populates="cliente")

class Pedido(Base):
    __tablename__ = "pedidos"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    numero_ticket = Column(String, index=True)
    fecha = Column(DateTime, default=datetime.utcnow)
    estado = Column(String, default="PENDIENTE") # PENDIENTE, PAGADO, COCINA, LISTO, CANCELADO
    total = Column(Float, default=0.0)
    metodo_pago = Column(String, nullable=True)
    cliente_id = Column(String(36), ForeignKey("clientes.id"), nullable=True)
    
    # Auditoría Fiscal
    base_imponible = Column(Float, default=0.0)
    iva_total = Column(Float, default=0.0)
    
    items = relationship("ItemPedido", back_populates="pedido")
    cliente = relationship("Cliente", back_populates="pedidos")

class ItemPedido(Base):
    __tablename__ = "item_pedido"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    pedido_id = Column(String(36), ForeignKey("pedidos.id"))
    producto_id = Column(String(36)) # ID literal para evitar dependencias circulares complejas en models
    cantidad = Column(Integer, default=1)
    precio_unitario = Column(Float)
    
    pedido = relationship("Pedido", back_populates="items")

class MovimientoStock(Base):
    __tablename__ = "movimientos_stock"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    producto_id = Column(String(36))
    cantidad = Column(Float)
    tipo = Column(String) # VENTA, COMPRA, MERMA, AJUSTE
    fecha = Column(DateTime, default=datetime.utcnow)
    motivo = Column(String, nullable=True)
