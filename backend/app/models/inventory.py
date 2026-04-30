import uuid
from sqlalchemy import Column, String, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship
from ..core.database import Base

class Ingrediente(Base):
    """Materia prima con trazabilidad de costes."""
    __tablename__ = "ingredientes"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = Column(String(100), nullable=False)
    unidad_medida = Column(String(20)) # kg, g, l, unidad
    coste_por_unidad = Column(Float, default=0.0)
    stock_actual = Column(Float, default=0.0)
    stock_minimo = Column(Float, default=0.0)

    # Relación con recetas
    recetas = relationship("RecetaItem", back_populates="ingrediente")

class RecetaItem(Base):
    """Relación muchos-a-muchos entre Productos e Ingredientes (Escandallo)."""
    __tablename__ = "receta_items"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    producto_id = Column(String(36), ForeignKey("productos.id"))
    ingrediente_id = Column(String(36), ForeignKey("ingredientes.id"))
    cantidad_necesaria = Column(Float, nullable=False)

    # Relaciones
    ingrediente = relationship("Ingrediente", back_populates="recetas")
    producto = relationship("Producto", back_populates="receta_items")
