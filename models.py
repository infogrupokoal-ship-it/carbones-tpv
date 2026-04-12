from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)  # MVP password
    rol = Column(String) # ADMIN, MANANA, TARDE

class Categoria(Base):
    __tablename__ = "categorias"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    orden = Column(Integer, default=0)
    productos = relationship("Producto", back_populates="categoria")
    is_synced = Column(Boolean, default=False)
    remote_id = Column(Integer, nullable=True)

class Producto(Base):
    __tablename__ = "productos"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    descripcion = Column(String, nullable=True)
    alergenos = Column(String, nullable=True)
    precio = Column(Float, default=0.0)
    impuesto = Column(Float, default=10.0) # 10.0 Comida, 21.0 Alcohol
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    is_synced = Column(Boolean, default=False)
    remote_id = Column(Integer, nullable=True)
    
    # Lógica Fraccional (Controla el inventario de un padre común)
    stock_actual = Column(Float, default=0)
    stock_base_id = Column(Integer, ForeignKey("productos.id"), nullable=True) # Si es un hijo (Ej. Cuarto Pollo) apunta a Pollo General
    factor_stock = Column(Float, default=1.0) # Cuanto resta al padre por unidad vendida
    
    categoria = relationship("Categoria", back_populates="productos")
    
class Cliente(Base):
    __tablename__ = "clientes"
    id = Column(Integer, primary_key=True, index=True)
    telefono = Column(String, unique=True, index=True)
    nombre = Column(String, nullable=True)
    nivel_fidelidad = Column(String, default="BRONCE") # BRONCE, PLATA, ORO
    visitas = Column(Integer, default=0)
    is_synced = Column(Boolean, default=False)
    remote_id = Column(Integer, nullable=True)
    preferencias = Column(String, nullable=True) # JSON de preferencias
    fecha_registro = Column(DateTime, default=datetime.now)
    
    pedidos = relationship("Pedido", back_populates="cliente")

class Pedido(Base):
    __tablename__ = "pedidos"
    id = Column(Integer, primary_key=True, index=True)
    numero_ticket = Column(String, index=True)
    fecha = Column(DateTime, default=datetime.now)
    estado = Column(String, default="PENDIENTE") # ESPERANDO_PAGO -> EN_PREPARACION -> LISTO
    origen = Column(String)
    total = Column(Float, default=0.0)
    cajero_username = Column(String, nullable=True) # Rastreo de turno
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=True)
    metodo_pago = Column(String, nullable=True) # EFECTIVO, TARJETA, MAQUINA
    descuento_aplicado = Column(Float, default=0.0)
    cubiertos_qty = Column(Integer, default=0)
    
    # Contabilidad Fiscal (Desglose legal de IVAs)
    base_imponible_10 = Column(Float, default=0.0)
    cuota_iva_10 = Column(Float, default=0.0)
    base_imponible_21 = Column(Float, default=0.0)
    cuota_iva_21 = Column(Float, default=0.0)
    
    # Campo para el Demonio Offline-First
    is_synced = Column(Boolean, default=False)
    remote_id = Column(Integer, nullable=True)
    
    # Geolocalización y Delivery
    tipo_entrega = Column(String, default="LOCAL") # LOCAL, RECOGIDA, DOMICILIO
    latitud_actual = Column(Float, nullable=True)
    longitud_actual = Column(Float, nullable=True)
    distancia_metros = Column(Float, nullable=True)
    
    items = relationship("ItemPedido", back_populates="pedido")
    cliente = relationship("Cliente", back_populates="pedidos")

class ItemPedido(Base):
    __tablename__ = "item_pedido"
    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"))
    producto_id = Column(Integer, ForeignKey("productos.id"))
    cantidad = Column(Integer, default=1)
    precio_unitario = Column(Float)
    is_synced = Column(Boolean, default=False)
    remote_id = Column(Integer, nullable=True)
    
    pedido = relationship("Pedido", back_populates="items")

class MovimientoStock(Base):
    __tablename__ = "movimientos_stock"
    id = Column(Integer, primary_key=True, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id"))
    cantidad = Column(Float) # Puede ser fracción
    tipo = Column(String) # PRODUCCION, VENTA
    fecha = Column(DateTime, default=datetime.now)
    origen_id = Column(Integer, nullable=True) # ID del pedido si es venta, o nulo si es produccion manual
    descripcion = Column(String, nullable=True)
    is_synced = Column(Boolean, default=False)
    remote_id = Column(Integer, nullable=True)
    
    producto = relationship("Producto", back_populates="movimientos")
