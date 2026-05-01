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
    pin_hash = Column(String(128))
    rol = Column(String(20), default="CASHIER") # ADMIN, MANAGER, CASHIER
    is_active = Column(Boolean, default=True)
    tienda_id = Column(String(36), ForeignKey("tiendas.id"))
    
    tienda = relationship("Tienda", back_populates="usuarios")

# --- CATÁLOGO & LOGÍSTICA ---
class Categoria(Base):
    __tablename__ = "categorias"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True)
    productos = relationship("Producto", back_populates="categoria")

class Producto(Base):
    __tablename__ = "productos"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(255))
    precio = Column(Float, nullable=False)
    impuesto = Column(Float, default=10.0)
    
    # Gestión de Stock Avanzada
    stock_actual = Column(Float, default=0.0)
    stock_minimo = Column(Float, default=0.0)
    stock_base_id = Column(String(36), ForeignKey("productos.id"), nullable=True) # Referencia al producto "Padre"
    factor_stock = Column(Float, default=1.0) # Cuanto resta del padre (ej: 0.25 para 1/4 de pollo)
    
    imagen_url = Column(String(255))
    alergenos = Column(String(255)) # Ej: "Gluten, Lactosa"
    info_nutricional = Column(Text) # JSON o Texto detallado
    categoria_id = Column(String(36), ForeignKey("categorias.id"))
    tienda_id = Column(String(36), ForeignKey("tiendas.id"))
    is_active = Column(Boolean, default=True)
    turno_disponible = Column(String(20), default="ALL") # ALL, MORNING, NIGHT
    
    categoria = relationship("Categoria", back_populates="productos")
    tienda = relationship("Tienda", back_populates="productos")
    receta_items = relationship("RecetaItem", back_populates="producto")

class Ingrediente(Base):
    __tablename__ = "ingredientes"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = Column(String(100), nullable=False)
    unidad_medida = Column(String(20), default="ud")
    stock_actual = Column(Float, default=0.0)
    stock_minimo = Column(Float, default=5.0)
    proveedor_id = Column(String(36), ForeignKey("proveedores.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    
    proveedor = relationship("Proveedor", back_populates="ingredientes")
    receta_items = relationship("RecetaItem", back_populates="ingrediente")

class Proveedor(Base):
    __tablename__ = "proveedores"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = Column(String(100), nullable=False)
    email = Column(String(100))
    telefono = Column(String(20))
    is_active = Column(Boolean, default=True)
    ingredientes = relationship("Ingrediente", back_populates="proveedor")

class RecetaItem(Base):
    __tablename__ = "receta_items"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    producto_id = Column(String(36), ForeignKey("productos.id"))
    ingrediente_id = Column(String(36), ForeignKey("ingredientes.id"))
    cantidad_necesaria = Column(Float, nullable=False)
    
    producto = relationship("Producto", back_populates="receta_items")
    ingrediente = relationship("Ingrediente", back_populates="receta_items")

# --- VENTAS & CONTABILIDAD ---
class Cliente(Base):
    __tablename__ = "clientes"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    telefono = Column(String(20), unique=True, index=True)
    nombre = Column(String(100))
    puntos_fidelidad = Column(Integer, default=0)
    nivel_fidelidad = Column(String(20), default="BRONCE")
    visitas = Column(Integer, default=0)

class VerificacionOTP(Base):
    __tablename__ = "verificaciones_otp"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    telefono = Column(String(20), index=True)
    codigo = Column(String(6))
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_expiracion = Column(DateTime)
    usado = Column(Boolean, default=False)

class Pedido(Base):
    __tablename__ = "pedidos"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    numero_ticket = Column(String(50), unique=True)
    fecha = Column(DateTime, default=datetime.utcnow)
    total = Column(Float, nullable=False)
    descuento_aplicado = Column(Float, default=0.0)
    
    base_imponible_10 = Column(Float, default=0.0)
    cuota_iva_10 = Column(Float, default=0.0)
    base_imponible_21 = Column(Float, default=0.0)
    cuota_iva_21 = Column(Float, default=0.0)
    
    metodo_pago = Column(String(20))
    estado = Column(String(20), default="ESPERANDO_PAGO")
    origen = Column(String(20), default="TPV")
    metodo_envio = Column(String(20), default="LOCAL") # LOCAL o DOMICILIO
    direccion = Column(Text, nullable=True)
    
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
    accion = Column(String(50))
    origen = Column(String(50))
    payload = Column(Text, nullable=True)
    procesado = Column(Boolean, default=False)

class LogOperativo(Base):
    __tablename__ = "logs_operativos"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    fecha = Column(DateTime, default=datetime.utcnow)
    nivel = Column(String(20))
    modulo = Column(String(50))
    mensaje = Column(Text)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    fecha = Column(DateTime, default=datetime.utcnow)
    usuario_id = Column(String(36), ForeignKey("usuarios.id"), nullable=True)
    accion = Column(String(100), nullable=False)
    entidad = Column(String(50))
    entidad_id = Column(String(36))
    ip_origen = Column(String(50))
    payload_previo = Column(Text, nullable=True)
    payload_nuevo = Column(Text, nullable=True)
    
    usuario = relationship("Usuario", backref="auditorias")

class ReporteZ(Base):
    __tablename__ = "reportes_z"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    fecha = Column(DateTime, default=datetime.utcnow)
    total_ventas = Column(Float)
    total_efectivo = Column(Float)
    total_tarjeta = Column(Float)
    efectivo_declarado = Column(Float, nullable=True)
    diferencia = Column(Float, default=0.0)
    pollos_vendidos = Column(Integer, default=0)
    coste_mermas = Column(Float, default=0.0)
    resumen_texto = Column(Text)

class MovimientoStock(Base):
    __tablename__ = "movimientos_stock"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    fecha = Column(DateTime, default=datetime.utcnow)
    producto_id = Column(String(36), ForeignKey("productos.id"), nullable=True)
    cantidad = Column(Float)
    tipo = Column(String(20))
    descripcion = Column(String(255))

class Review(Base):
    __tablename__ = "reviews"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    fecha = Column(DateTime, default=datetime.utcnow)
    rating = Column(Integer)
    comentario = Column(Text)
    cliente_id = Column(String(36), ForeignKey("clientes.id"), nullable=True)

class Fichaje(Base):
    __tablename__ = "fichajes"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    usuario_id = Column(String(36), ForeignKey("usuarios.id"))
    tipo = Column(String(20)) # ENTRADA, SALIDA, INICIO_PAUSA, FIN_PAUSA
    fecha = Column(DateTime, default=datetime.utcnow)
    
    usuario = relationship("Usuario", backref="fichajes")

class Merma(Base):
    __tablename__ = "mermas"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    fecha = Column(DateTime, default=datetime.utcnow)
    entidad_tipo = Column(String(20)) # PRODUCTO o INGREDIENTE
    entidad_id = Column(String(36)) # ID de Producto o Ingrediente
    cantidad = Column(Float, nullable=False)
    motivo = Column(String(100)) # CADUCADO, ERROR_COCINA, ROTURA
    coste_estimado = Column(Float, default=0.0)
    usuario_id = Column(String(36), ForeignKey("usuarios.id"))
