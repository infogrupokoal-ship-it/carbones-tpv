import uuid
from sqlalchemy import Column, Float, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import relationship
from ..core.database import Base

class Categoria(Base):
    __tablename__ = "categorias"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = Column(String, index=True)
    orden = Column(Integer, default=0)
    productos = relationship("Producto", back_populates="categoria")

class Producto(Base):
    __tablename__ = "productos"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = Column(String, index=True)
    descripcion = Column(String, nullable=True)
    precio = Column(Float, default=0.0)
    coste_estimado = Column(Float, default=0.0)
    url_imagen = Column(String, nullable=True)
    categoria_id = Column(String(36), ForeignKey("categorias.id"))
    is_active = Column(Boolean, default=True)
    
    # Lógica de Stock
    stock_actual = Column(Float, default=0)
    stock_minimo = Column(Float, default=0)
    
    categoria = relationship("Categoria", back_populates="productos")
    receta_items = relationship("Receta", back_populates="producto")

class Proveedor(Base):
    __tablename__ = "proveedores"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = Column(String, index=True)
    telefono = Column(String, nullable=True)
    email = Column(String, nullable=True)
    ingredientes = relationship("Ingrediente", back_populates="proveedor")

class Ingrediente(Base):
    __tablename__ = "ingredientes"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = Column(String, index=True)
    unidad = Column(String) # KG, L, UD
    coste_unitario = Column(Float, default=0.0)
    proveedor_id = Column(String(36), ForeignKey("proveedores.id"))
    
    proveedor = relationship("Proveedor", back_populates="ingredientes")
    recetas = relationship("Receta", back_populates="ingrediente")

class Receta(Base):
    __tablename__ = "recetas"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    producto_id = Column(String(36), ForeignKey("productos.id"))
    ingrediente_id = Column(String(36), ForeignKey("ingredientes.id"))
    cantidad = Column(Float, default=1.0)
    
    producto = relationship("Producto", back_populates="receta_items")
    ingrediente = relationship("Ingrediente", back_populates="recetas")
