import uuid
from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship
from ..core.database import Base

class Tienda(Base):
    """Modelo Maestro para la arquitectura Multi-Tienda (SaaS)."""
    __tablename__ = "tiendas"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = Column(String(100), nullable=False)
    direccion = Column(String(255))
    telefono = Column(String(20))
    is_active = Column(Boolean, default=True)
    
    # Relaciones
    usuarios = relationship("Usuario", back_populates="tienda")
    productos = relationship("Producto", back_populates="tienda")
    pedidos = relationship("Pedido", back_populates="tienda")
