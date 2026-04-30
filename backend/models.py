import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Integer, Boolean, Text
from sqlalchemy.orm import relationship
from .database import Base

# --- DOMINIO TIENDA ---
class Tienda(Base):
    __tablename__ = "tiendas"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = Column(String(100), nullable=False)
    direccion = Column(String(255))
    telefono = Column(String(20))
    is_active = Column(Boolean, default=True)
    
    usuarios = relationship("Usuario", back_populates="tienda")
    productos = relationship("Producto", back_populates="tienda")
    pedidos = relationship("Pedido", back_populates="tienda")

# --- DOMINIO USUARIOS ---
class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, index=True)
    full_name = Column(String(100))
    pin_hash = Column(String(128))
    hashed_password = Column(String(128), nullable=True)
    rol = Column(String(20), default="CASHIER") # ADMIN, MANAGER, CASHIER
    is_active = Column(Boolean, default=True)
    tienda_id = Column(String(36), ForeignKey("tiendas.id"))
    
    tienda = relationship("Tienda", back_populates="usuarios")

# --- DOMINIO PRODUCTOS & INVENTARIO ---
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
    tienda_id = Column(String(36), ForeignKey("tiendas.id"))
    is_active = Column(Boolean, default=True)
    
    categoria = relationship("Categoria", back_populates="productos")
    tienda = relationship("Tienda", back_populates="productos")
    receta_items = relationship("RecetaItem", back_populates="producto")

class Ingrediente(Base):
    __tablename__ = "ingredientes"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = Column(String(100), nullable=False)
    unidad_medida = Column(String(20)) # kg, l, ud
    coste_por_unidad = Column(Float, default=0.0)
    stock_actual = Column(Float, default=0.0)
    
    receta_items = relationship("RecetaItem", back_populates="ingrediente")

class RecetaItem(Base):
    __tablename__ = "receta_items"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    producto_id = Column(String(36), ForeignKey("productos.id"))
    ingrediente_id = Column(String(36), ForeignKey("ingredientes.id"))
    cantidad_necesaria = Column(Float, nullable=False)
    
    producto = relationship("Producto", back_populates="receta_items")
    ingrediente = relationship("Ingrediente", back_populates="receta_items")

# --- DOMINIO TRANSACCIONAL ---
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
    metodo_pago = Column(String(20)) # EFECTIVO, TARJETA
    estado = Column(String(20), default="COMPLETADO")
    cliente_id = Column(String(36), ForeignKey("clientes.id"), nullable=True)
    tienda_id = Column(String(36), ForeignKey("tiendas.id"))

    items = relationship("ItemPedido", back_populates="pedido")
    tienda = relationship("Tienda", back_populates="pedidos")

class ItemPedido(Base):
    __tablename__ = "item_pedido"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    pedido_id = Column(String(36), ForeignKey("pedidos.id"))
    producto_id = Column(String(36))
    cantidad = Column(Integer, default=1)
    precio_unitario = Column(Float)
    
    pedido = relationship("Pedido", back_populates="items")

# --- DOMINIO AUDITORÍA ---
class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    fecha = Column(DateTime, default=datetime.utcnow)
    usuario_id = Column(String(36))
    accion = Column(String(100))
    detalles = Column(Text)
    ip_address = Column(String(45))
