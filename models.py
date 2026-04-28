from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import uuid

Base = declarative_base()

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)  # MVP password
    rol = Column(String) # ADMIN, MANANA, TARDE
    fichajes = relationship("Fichaje", back_populates="usuario")

class Fichaje(Base):
    __tablename__ = "fichajes"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    usuario_id = Column(String(36), ForeignKey("usuarios.id"))
    tipo = Column(String) # ENTRADA, SALIDA, INICIO_PAUSA, FIN_PAUSA
    fecha = Column(DateTime, default=datetime.now)
    usuario = relationship("Usuario", back_populates="fichajes")

class Categoria(Base):
    __tablename__ = "categorias"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    nombre = Column(String, index=True)
    orden = Column(Integer, default=0)
    productos = relationship("Producto", back_populates="categoria")
    is_synced = Column(Boolean, default=False)
    remote_id = Column(String(36), nullable=True)

class Producto(Base):
    __tablename__ = "productos"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    nombre = Column(String, index=True)
    descripcion = Column(String, nullable=True)
    url_imagen = Column(String, nullable=True)
    alergenos = Column(String, nullable=True)
    precio = Column(Float, default=0.0)
    impuesto = Column(Float, default=10.0) # 10.0 Comida, 21.0 Alcohol
    categoria_id = Column(String(36), ForeignKey("categorias.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    is_synced = Column(Boolean, default=False)
    remote_id = Column(String(36), nullable=True)
    
    # Lógica Fraccional (Controla el inventario de un padre común)
    stock_actual = Column(Float, default=0)
    stock_minimo = Column(Float, default=0) # Umbral de alerta
    stock_base_id = Column(String(36), ForeignKey("productos.id"), nullable=True) # Si es un hijo (Ej. Cuarto Pollo) apunta a Pollo General
    factor_stock = Column(Float, default=1.0) # Cuanto resta al padre por unidad vendida
    
    # Lógica de Complementos y Alérgenos
    is_addon = Column(Boolean, default=False)
    alergenos = Column(String, nullable=True) # Lista separada por comas (Ej. "Gluten, Lácteos")
    
    categoria = relationship("Categoria", back_populates="productos")
    movimientos = relationship("MovimientoStock", back_populates="producto")
    receta_items = relationship("Receta", back_populates="producto")

class Proveedor(Base):
    __tablename__ = "proveedores"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    nombre = Column(String, index=True)
    telefono = Column(String, nullable=True)
    email = Column(String, nullable=True)
    dias_entrega = Column(String, nullable=True) # Ej: "Lunes, Jueves"
    ingredientes = relationship("Ingrediente", back_populates="proveedor")

class Ingrediente(Base):
    __tablename__ = "ingredientes"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    nombre = Column(String, index=True)
    unidad_medida = Column(String) # KG, UD, LITRO
    stock_actual = Column(Float, default=0.0)
    stock_minimo = Column(Float, default=0.0)
    coste_unitario = Column(Float, default=0.0)
    proveedor_id = Column(String(36), ForeignKey("proveedores.id"), nullable=True)
    
    proveedor = relationship("Proveedor", back_populates="ingredientes")
    recetas = relationship("Receta", back_populates="ingrediente")

class Receta(Base):
    __tablename__ = "recetas"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    producto_id = Column(String(36), ForeignKey("productos.id"))
    ingrediente_id = Column(String(36), ForeignKey("ingredientes.id"))
    cantidad_necesaria = Column(Float, default=1.0)
    
    producto = relationship("Producto", back_populates="receta_items")
    ingrediente = relationship("Ingrediente", back_populates="recetas")
    
class Cliente(Base):
    __tablename__ = "clientes"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    telefono = Column(String, unique=True, index=True)
    wa_id = Column(String, unique=True, index=True, nullable=True) # WhatsApp ID
    estado_registro = Column(String, default="COMPLETADO") # PENDIENTE_NOMBRE, COMPLETADO
    nombre = Column(String, nullable=True)
    nivel_fidelidad = Column(String, default="BRONCE") # BRONCE, PLATA, ORO
    puntos_fidelidad = Column(Integer, default=0) # 1 punto = 1 euro
    visitas = Column(Integer, default=0)
    is_synced = Column(Boolean, default=False)
    remote_id = Column(String(36), nullable=True)
    preferencias = Column(String, nullable=True) # JSON de preferencias
    fecha_registro = Column(DateTime, default=datetime.now)
    
    pedidos = relationship("Pedido", back_populates="cliente")

class Pedido(Base):
    __tablename__ = "pedidos"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    numero_ticket = Column(String, index=True)
    fecha = Column(DateTime, default=datetime.now)
    estado = Column(String, default="PENDIENTE") # ESPERANDO_PAGO -> EN_PREPARACION -> LISTO
    origen = Column(String)
    total = Column(Float, default=0.0)
    cajero_username = Column(String, nullable=True) # Rastreo de turno
    cliente_id = Column(String(36), ForeignKey("clientes.id"), nullable=True)
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
    remote_id = Column(String(36), nullable=True)
    
    # Geolocalización y Delivery
    tipo_entrega = Column(String, default="LOCAL") # LOCAL, RECOGIDA, DOMICILIO
    latitud_actual = Column(Float, nullable=True)
    longitud_actual = Column(Float, nullable=True)
    distancia_metros = Column(Float, nullable=True)
    
    # Pagos Online
    stripe_session_id = Column(String, nullable=True)
    
    # Comentarios de Cocina/Cliente
    notas_cliente = Column(String, nullable=True)
    
    items = relationship("ItemPedido", back_populates="pedido")
    cliente = relationship("Cliente", back_populates="pedidos")

class ItemPedido(Base):
    __tablename__ = "item_pedido"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    pedido_id = Column(String(36), ForeignKey("pedidos.id"))
    producto_id = Column(String(36), ForeignKey("productos.id"))
    cantidad = Column(Integer, default=1)
    precio_unitario = Column(Float)
    is_synced = Column(Boolean, default=False)
    remote_id = Column(String(36), nullable=True)
    
    pedido = relationship("Pedido", back_populates="items")

class MovimientoStock(Base):
    __tablename__ = "movimientos_stock"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    producto_id = Column(String(36), ForeignKey("productos.id"))
    cantidad = Column(Float) # Puede ser fracción
    tipo = Column(String) # PRODUCCION, VENTA
    fecha = Column(DateTime, default=datetime.now)
    origen_id = Column(String(36), nullable=True) # ID del pedido si es venta, o nulo si es produccion manual
    descripcion = Column(String, nullable=True)
    is_synced = Column(Boolean, default=False)
    remote_id = Column(String(36), nullable=True)
    
    producto = relationship("Producto", back_populates="movimientos")

class HardwareCommand(Base):
    __tablename__ = "hardware_commands"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    accion = Column(String) # Ejemplo: "abrir_caja"
    origen = Column(String) # Ejemplo: "app_movil_jefe"
    estado = Column(String, default="PENDIENTE") # PENDIENTE, EJECUTADO
    payload = Column(String, nullable=True) # JSON de datos del ticket
    fecha_creacion = Column(DateTime, default=datetime.now)
    fecha_ejecucion = Column(DateTime, nullable=True)

class ReporteZ(Base):
    __tablename__ = "reportes_z"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    fecha_cierre = Column(DateTime, default=datetime.now)
    total_efectivo = Column(Float, default=0.0)
    total_tarjeta = Column(Float, default=0.0)
    total_caja = Column(Float, default=0.0)
    
    # Arqueo Ciego
    efectivo_declarado = Column(Float, default=0.0)
    diferencia_arqueo = Column(Float, default=0.0)
    
    pollos_vendidos = Column(Integer, default=0)
    coste_mermas = Column(Float, default=0.0) # Perdida estimada
    resumen_texto = Column(String) # Backup de lo que se envia por WA

class Review(Base):
    __tablename__ = "reviews"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    pedido_id = Column(String(36), ForeignKey("pedidos.id"), nullable=True)
    cliente_id = Column(String(36), ForeignKey("clientes.id"), nullable=True)
    rating = Column(Integer, default=5) # 1 a 5 estrellas
    comentario = Column(String, nullable=True)
    fecha = Column(DateTime, default=datetime.now)
    analisis_ia = Column(String, nullable=True) # Resumen/Tag generado por IA
    
    pedido = relationship("Pedido")
    cliente = relationship("Cliente")
