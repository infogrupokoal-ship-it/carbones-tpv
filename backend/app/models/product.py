import uuid
from sqlalchemy import Column, String, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from ..core.database import Base

class Categoria(Base):
    __tablename__ = "categorias"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = Column(String(50), nullable=False)
    productos = relationship("Producto", back_populates="categoria")

class Producto(Base):
    __tablename__ = "productos"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(255))
    precio = Column(Float, nullable=False)
    coste_estimado = Column(Float, default=0.0)
    categoria_id = Column(String(36), ForeignKey("categorias.id"))
    is_active = Column(Boolean, default=True)
    
    # Relaciones
    categoria = relationship("Categoria", back_populates="productos")
    receta_items = relationship("RecetaItem", back_populates="producto")
