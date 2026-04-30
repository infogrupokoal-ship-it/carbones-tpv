import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Integer, Boolean, Text
from sqlalchemy.orm import relationship
from .database import Base

# --- GESTIÓN DE TIENDA & MULTI-TENANCY ---
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

# --- CONTROL DE ACCESO & PERSONAL ---
class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, index=True)
    full_name = Column(String(100))
    pin_hash = Column(String(128)) # Hash del PIN de 4 dígitos
    rol = Column(String(20), default="CASHIER") # ADMIN, MANAGER, CASHIER
    is_active = Column(Boolean, default=True)
    tienda_id = Column(String(36), ForeignKey("tiendas.id"))
    
    tienda = relationship("Tienda", back_populates="usuarios")

# --- CATÁLOGO & LOGÍSTICA ---
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
    impuesto = Column(Float, default=10.0) # 10.0 (Comida), 21.0 (Bebida/Alcohol)
    stock_actual = Column(Float, default=0.0)
    imagen_url = Column(String(255))
    categoria_id = Column(String(36), ForeignKey("categorias.id"))
    tienda_id = Column(String(36), ForeignKey("tiendas.id"))
    is_active = Column(Boolean, default=True)
    
    categoria = relationship("Categoria", back_populates="productos")
    tienda = relationship("Tienda", back_populates="productos")

class Ingrediente(Base):
    __tablename__ = "ingredientes"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = Column(String(100), nullable=False)
    unidad_medida = Column(String(20), default="ud") # kg, l, ud
    stock_actual = Column(Float, default=0.0)
    stock_minimo = Column(Float, default=5.0)
    proveedor_id = Column(String(36), ForeignKey("proveedores.id"), nullable=True)
    
    proveedor = relationship("Proveedor", back_populates="ingredientes")

class Proveedor(Base):
    __tablename__ = "proveedores"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = Column(String(100), nullable=False)
    email = Column(String(100))
    telefono = Column(String(20))
    ingredientes = relationship("Ingrediente", back_populates="proveedor")

# --- VENTAS & CONTABILIDAD ---
class Cliente(Base):
    __tablename__ = "clientes"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    telefono = Column(String(20), unique=True, index=True)
    nombre = Column(String(100))
    puntos_fidelidad = Column(Integer, default=0)
    nivel_fidelidad = Column(String(20), default="BRONCE") # BRONCE, PLATA, ORO
    visitas = Column(Integer, default=0)

class Pedido(Base):
    __tablename__ = "pedidos"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    numero_ticket = Column(String(50), unique=True)
    fecha = Column(DateTime, default=datetime.utcnow)
    total = Column(Float, nullable=False)
    descuento_aplicado = Column(Float, default=0.0)
    
    # Desglose Fiscal Legal (España)
    base_imponible_10 = Column(Float, default=0.0)
    cuota_iva_10 = Column(Float, default=0.0)
    base_imponible_21 = Column(Float, default=0.0)
    cuota_iva_21 = Column(Float, default=0.0)
    
    metodo_pago = Column(String(20)) # EFECTIVO, TARJETA, BIZUM
    estado = Column(String(20), default="ESPERANDO_PAGO") # PENDIENTE, EN_PREPARACION, COMPLETADO, CANCELADO
    origen = Column(String(20), default="TPV") # TPV, WEB, APP, QUIOSCO
    
    notas_cliente = Column(Text)
    cubiertos_qty = Column(Integer, default=0)
    
    cliente_id = Column(String(36), ForeignKey("clientes.id"), nullable=True)
    tienda_id = Column(String(36), ForeignKey("tiendas.id"))
    
    items = relationship("ItemPedido", back_populates="pedido")
    tienda = relationship("Tienda", back_populates="pedidos")

class ItemPedido(Base):
    __tablename__ = "item_pedido"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    pedido_id = Column(String(36), ForeignKey("pedidos.id"))
    producto_id = Column(String(36), ForeignKey("productos.id"))
    cantidad = Column(Integer, default=1)
    precio_unitario = Column(Float)
    
    pedido = relationship("Pedido", back_populates="items")

# --- HARDWARE & OPERATIVA ---
class HardwareCommand(Base):
    __tablename__ = "hardware_commands"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    fecha = Column(DateTime, default=datetime.utcnow)
    accion = Column(String(50)) # imprimir, abrir_caja
    origen = Column(String(50))
    payload = Column(Text, nullable=True) # JSON con datos de impresión
    procesado = Column(Boolean, default=False)

class LogOperativo(Base):
    __tablename__ = "logs_operativos"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    fecha = Column(DateTime, default=datetime.utcnow)
    nivel = Column(String(20)) # INFO, WARNING, ERROR
    modulo = Column(String(50))
    mensaje = Column(Text)

class ReporteZ(Base):
    __tablename__ = "reportes_z"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    fecha = Column(DateTime, default=datetime.utcnow)
    total_ventas = Column(Float)
    total_efectivo = Column(Float)
    total_tarjeta = Column(Float)
    efectivo_declarado = Column(Float, nullable=True)
    diferencia = Column(Float, default=0.0)

class MovimientoStock(Base):
    __tablename__ = "movimientos_stock"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    fecha = Column(DateTime, default=datetime.utcnow)
    producto_id = Column(String(36), ForeignKey("productos.id"), nullable=True)
    cantidad = Column(Float)
    tipo = Column(String(20)) # VENTA, MERMA, PRODUCCION, ENTRADA_PROVEEDOR, SOBRANTE_DIA
    descripcion = Column(String(255))
