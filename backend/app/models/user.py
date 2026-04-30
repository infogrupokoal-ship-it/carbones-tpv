import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from ..core.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, index=True)
    full_name = Column(String(100))
    pin_hash = Column(String(128))
    hashed_password = Column(String(128), nullable=True)
    rol = Column(String(20), default="CASHIER")
    is_active = Column(Boolean, default=True)
    tienda_id = Column(String(36), ForeignKey("tiendas.id"), nullable=True)
    
    # Relaciones
    tienda = relationship("Tienda", back_populates="usuarios")
