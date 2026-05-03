import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Integer, Boolean, Text, JSON
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
    horarios = relationship("Horario", back_populates="tienda")
    
    # Configuración Industrial
    logo_url = Column(String(255))
    color_primario = Column(String(20), default="#f59e0b")
    mensaje_ticket = Column(Text)
    lat = Column(Float)
    lon = Column(Float)
    radio_entrega_km = Column(Float, default=5.0)

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
    imagen_url = Column(String(255), nullable=True)
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
    precio_base = Column(Float, default=0.0) # Precio original sin ajustes dinámicos
    
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
    fecha_creacion = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    fecha_expiracion = Column(DateTime)
    usado = Column(Boolean, default=False)

class Pedido(Base):
    __tablename__ = "pedidos"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    numero_ticket = Column(String(50), unique=True)
    fecha = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
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
    repartidor_id = Column(String(36), ForeignKey("usuarios.id"), nullable=True)
    
    # Integración Stripe & Pagos Online
    stripe_session_id = Column(String(255), nullable=True)
    stripe_payment_status = Column(String(50), nullable=True) # pending, paid, failed
    external_payment_id = Column(String(255), nullable=True)
    
    is_synced = Column(Boolean, default=False)
    
    items = relationship("ItemPedido", back_populates="pedido")
    tienda = relationship("Tienda", back_populates="pedidos")
    cliente = relationship("Cliente")

    @property
    def cliente_nombre(self):
        return self.cliente.nombre if self.cliente else "Anónimo"

    @property
    def cliente_telefono(self):
        return self.cliente.telefono if self.cliente else None

class ItemPedido(Base):
    __tablename__ = "item_pedido"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    pedido_id = Column(String(36), ForeignKey("pedidos.id"))
    producto_id = Column(String(36), ForeignKey("productos.id"))
    cantidad = Column(Integer, default=1)
    precio_unitario = Column(Float)
    
    pedido = relationship("Pedido", back_populates="items")
    producto = relationship("Producto")

    @property
    def nombre(self):
        return self.producto.nombre if self.producto else "Producto Desconocido"
    
    @property
    def precio(self):
        return self.precio_unitario

# --- HARDWARE & OPERATIVA ---
class HardwareCommand(Base):
    __tablename__ = "hardware_commands"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    fecha = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    accion = Column(String(50))
    origen = Column(String(50))
    payload = Column(Text, nullable=True)
    procesado = Column(Boolean, default=False)
    estado = Column(String(20), default="PENDIENTE") # PENDIENTE, EJECUTADO, FALLIDO
    fecha_ejecucion = Column(DateTime, nullable=True)

class LogOperativo(Base):
    __tablename__ = "logs_operativos"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    fecha = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    nivel = Column(String(20))
    modulo = Column(String(50))
    mensaje = Column(Text)

class TareaOperativa(Base):
    __tablename__ = "tareas_operativas"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    fecha = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    titulo = Column(String(100), nullable=False)
    descripcion = Column(Text)
    prioridad = Column(String(20), default="MEDIA") # BAJA, MEDIA, ALTA, CRITICA
    estado = Column(String(20), default="PENDIENTE") # PENDIENTE, COMPLETADO
    usuario_id = Column(String(36), ForeignKey("usuarios.id"), nullable=True)
    tienda_id = Column(String(36), ForeignKey("tiendas.id"))


class ReporteZ(Base):
    __tablename__ = "reportes_z"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    fecha = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
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
    fecha = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    producto_id = Column(String(36), ForeignKey("productos.id"), nullable=True)
    cantidad = Column(Float)
    tipo = Column(String(20))
    descripcion = Column(String(255))

class Review(Base):
    __tablename__ = "reviews"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    fecha = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    rating = Column(Integer)
    comentario = Column(Text)
    cliente_id = Column(String(36), ForeignKey("clientes.id"), nullable=True)

class Fichaje(Base):
    __tablename__ = "fichajes"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    usuario_id = Column(String(36), ForeignKey("usuarios.id"))
    tipo = Column(String(20)) # ENTRADA, SALIDA, INICIO_PAUSA, FIN_PAUSA
    fecha = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    
    usuario = relationship("Usuario", backref="fichajes")

class Merma(Base):
    __tablename__ = "mermas"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    fecha = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    entidad_tipo = Column(String(20)) # PRODUCTO o INGREDIENTE
    entidad_id = Column(String(36)) # ID de Producto o Ingrediente
    cantidad = Column(Float, nullable=False)
    motivo = Column(String(100)) # CADUCADO, ERROR_COCINA, ROTURA
    coste_estimado = Column(Float, default=0.0)
    usuario_id = Column(String(36), ForeignKey("usuarios.id"))

# --- INFRAESTRUCTURA ENTERPRISE ---
class Horario(Base):
    __tablename__ = "horarios"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tienda_id = Column(String(36), ForeignKey("tiendas.id"))
    dia_semana = Column(Integer) # 0-6 (Lunes-Domingo)
    hora_apertura = Column(String(5)) # "09:00"
    hora_cierre = Column(String(5)) # "22:00"
    is_closed = Column(Boolean, default=False)
    
    tienda = relationship("Tienda", back_populates="horarios")

class Notificacion(Base):
    __tablename__ = "notificaciones"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tipo = Column(String(20)) # WHATSAPP, EMAIL, PUSH
    destino = Column(String(100))
    asunto = Column(String(255))
    mensaje = Column(Text)
    estado = Column(String(20), default="PENDIENTE") # PENDIENTE, ENVIADO, ERROR
    reintentos = Column(Integer, default=0)
    fecha_creacion = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    fecha_envio = Column(DateTime, nullable=True)

class Traduccion(Base):
    __tablename__ = "traducciones"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    clave = Column(String(100), index=True)
    idioma = Column(String(5), default="es")
    valor = Column(Text)

# --- FLUJO COMERCIAL & MARKETING (PHASE 2) ---
class Presupuesto(Base):
    __tablename__ = "presupuestos"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    numero_presupuesto = Column(String(50), unique=True)
    fecha = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    fecha_validez = Column(DateTime)
    total = Column(Float, nullable=False)
    estado = Column(String(20), default="BORRADOR") # BORRADOR, ENVIADO, ACEPTADO, RECHAZADO, VENCIDO
    notas = Column(Text)
    
    cliente_id = Column(String(36), ForeignKey("clientes.id"), nullable=True)
    tienda_id = Column(String(36), ForeignKey("tiendas.id"))
    
    items = relationship("ItemPresupuesto", back_populates="presupuesto")
    cliente = relationship("Cliente")

class ItemPresupuesto(Base):
    __tablename__ = "item_presupuesto"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    presupuesto_id = Column(String(36), ForeignKey("presupuestos.id"))
    producto_id = Column(String(36), ForeignKey("productos.id"))
    cantidad = Column(Integer, default=1)
    precio_unitario = Column(Float)
    
    presupuesto = relationship("Presupuesto", back_populates="items")
    producto = relationship("Producto")

class Referido(Base):
    __tablename__ = "referidos"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    cliente_referidor_id = Column(String(36), ForeignKey("clientes.id"))
    cliente_referido_id = Column(String(36), ForeignKey("clientes.id"))
    fecha = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    estado = Column(String(20), default="PENDIENTE") # PENDIENTE, COMPLETADO
    bono_aplicado = Column(Float, default=0.0)
    
    referidor = relationship("Cliente", foreign_keys=[cliente_referidor_id])
    referido = relationship("Cliente", foreign_keys=[cliente_referido_id])

class WhatsAppTemplate(Base):
    __tablename__ = "whatsapp_templates"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = Column(String(50), unique=True)
    slug = Column(String(50), unique=True)
    contenido = Column(Text)
    variables = Column(String(255)) # Comma separated list of variables: "nombre,ticket,total"
    is_active = Column(Boolean, default=True)

# --- LOGÍSTICA & RRHH AVANZADO (PHASE 3) ---
class AsignacionReparto(Base):
    __tablename__ = "asignaciones_reparto"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    pedido_id = Column(String(36), ForeignKey("pedidos.id"))
    repartidor_id = Column(String(36), ForeignKey("usuarios.id"))
    fecha_asignacion = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    fecha_entrega = Column(DateTime, nullable=True)
    estado = Column(String(20), default="EN_CAMINO") # EN_CAMINO, ENTREGADO, FALLIDO
    
    pedido = relationship("Pedido")
    repartidor = relationship("Usuario")

class Liquidacion(Base):
    __tablename__ = "liquidaciones"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    usuario_id = Column(String(36), ForeignKey("usuarios.id"))
    fecha_inicio = Column(DateTime)
    fecha_fin = Column(DateTime)
    total_pedidos = Column(Integer, default=0)
    monto_fijo = Column(Float, default=0.0)
    comisiones = Column(Float, default=0.0)
    total_pagar = Column(Float, default=0.0)
    estado = Column(String(20), default="PENDIENTE") # PENDIENTE, PAGADA
    
    usuario = relationship("Usuario")

# --- ENTERPRISE SINGULARITY V9.0 (ULTRA-INDUSTRIAL) ---

class GhostBrand(Base):
    __tablename__ = "ghost_brands"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = Column(String(100), nullable=False)
    slug = Column(String(50), unique=True)
    is_active = Column(Boolean, default=True)
    config_json = Column(Text) # Estética, menús específicos, integraciones
    tienda_id = Column(String(36), ForeignKey("tiendas.id"))
    tienda = relationship("Tienda")

class RoboticsTelemetry(Base):
    __tablename__ = "robotics_telemetry"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    fecha = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    device_id = Column(String(50), index=True)
    sensor_type = Column(String(50)) # TEMP_FRAYER, OIL_QUALITY, DISPENSE_COUNT
    value = Column(Float)
    unit = Column(String(20))
    status = Column(String(20)) # OK, WARNING, ERROR

class ESGMétrics(Base):
    __tablename__ = "esg_metrics"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    fecha = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    tienda_id = Column(String(36), ForeignKey("tiendas.id"))
    co2_saved_kg = Column(Float, default=0.0)
    food_waste_kg = Column(Float, default=0.0)
    plastic_reduced_kg = Column(Float, default=0.0)
    energy_kwh = Column(Float, default=0.0)
    water_liters = Column(Float, default=0.0)

class YieldRule(Base):
    __tablename__ = "yield_rules"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = Column(String(100))
    condicion_clima = Column(String(50)) # RAIN, SUN, HEAT
    condicion_demanda = Column(String(20)) # HIGH, LOW, NORMAL
    ajuste_precio_pct = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)

class QSCAudit(Base):
    __tablename__ = "qsc_audits"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    fecha = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    tienda_id = Column(String(36), ForeignKey("tiendas.id"))
    auditor_id = Column(String(36), ForeignKey("usuarios.id"))
    score_calidad = Column(Float) # 0-100
    score_servicio = Column(Float)
    score_limpieza = Column(Float)
    observaciones = Column(Text)
    fotos_url = Column(Text) # CSV of URLs

class FinancialSnapshot(Base):
    __tablename__ = "financial_snapshots"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    fecha = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    revenue = Column(Float)
    ebitda = Column(Float)
    burn_rate = Column(Float)
    cac = Column(Float) # Coste Adquisición Cliente
    ltv = Column(Float) # Life Time Value
    runway_months = Column(Integer)

class FranchiseContract(Base):
    __tablename__ = "franchise_contracts"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    franquiciado_nombre = Column(String(100))
    tienda_id = Column(String(36), ForeignKey("tiendas.id"))
    fecha_inicio = Column(DateTime)
    fecha_fin = Column(DateTime)
    canon_mensual = Column(Float)
    royalties_pct = Column(Float)
    estado = Column(String(20)) # VIGENTE, SUSPENDIDO, FINALIZADO

class CallInteraction(Base):
    __tablename__ = "call_interactions"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    fecha = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    telefono_cliente = Column(String(20))
    duracion_seg = Column(Integer)
    sentimiento = Column(String(20)) # POSITIVE, NEUTRAL, NEGATIVE
    resumen_ia = Column(Text)
    pedido_generado_id = Column(String(36), ForeignKey("pedidos.id"), nullable=True)

class MenuPerformance(Base):
    __tablename__ = "menu_performance"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    producto_id = Column(String(36), ForeignKey("productos.id"))
    popularity_index = Column(Float) # 0-1
    margin_contribution = Column(Float)
    classification = Column(String(20)) # STAR, PLOWHORSE, PUZZLE, DOG (Matrix BC)

class BatchTraceability(Base):
    __tablename__ = "batch_traceability"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    lote_id = Column(String(50), unique=True)
    ingrediente_id = Column(String(36), ForeignKey("ingredientes.id"))
    fecha_recepcion = Column(DateTime)
    fecha_caducidad = Column(DateTime)
    temperatura_recepcion = Column(Float)
    blockchain_hash = Column(String(128))
    status = Column(String(20)) # OK, QUARANTINE, REJECTED

class AIConfig(Base):
    __tablename__ = "ai_configs"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    clave = Column(String(50), unique=True)
    valor = Column(Text)
    description = Column(String(255))

class GlobalState(Base):
    __tablename__ = "global_state"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    key = Column(String(50), unique=True)
    value = Column(Text)
    last_updated = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

# --- AUDITORÍA & SEGURIDAD INDUSTRIAL ---
class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    user_id = Column(String(36), ForeignKey("usuarios.id"), nullable=True)
    action = Column(String(100), nullable=False)
    resource = Column(String(50))
    resource_id = Column(String(36))
    ip_address = Column(String(50))
    details = Column(Text, nullable=True)
    
    usuario = relationship("Usuario", backref="auditorias")

# --- MULTIMEDIA & IA ---
class Attachment(Base):
    __tablename__ = "attachments"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Core Identification
    project = Column(String(50), nullable=False, default="carbones_tpv") # 'gestion_koal', 'carbones_tpv'
    source = Column(String(50), nullable=False, default="web") # whatsapp, telegram, web, email, drive
    entity_type = Column(String(50), nullable=False) # 'client', 'job', 'quote', 'invoice', 'provider', etc
    entity_id = Column(String(36), nullable=False)
    
    # File Metadata
    original_filename = Column(String(255), nullable=False)
    safe_filename = Column(String(255), nullable=False)
    mime_type = Column(String(100), nullable=False)
    size_bytes = Column(Integer, nullable=False)
    sha256 = Column(String(64), nullable=False, index=True) # Checksum real SHA-256
    
    # Storage
    file_url = Column(String(500), nullable=False)
    storage_path = Column(String(500), nullable=False)
    
    # Ownership
    uploaded_by = Column(String(36), ForeignKey("usuarios.id"), nullable=True)
    phone_number = Column(String(50), nullable=True) # Para WhatsApp/Telegram sender
    
    # Security and Lifecycle
    status = Column(String(50), default="received") # received, stored, analyzed, failed, needs_review
    is_sensitive = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    preview_available = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    # IA Meta
    ai_summary = Column(Text)
    ocr_text = Column(Text)
    labels = Column(String(255)) # Tagging IA

    uploader = relationship("Usuario", foreign_keys=[uploaded_by])

class Multimedia(Base):
    __tablename__ = "multimedia"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    original_name = Column(String(255), nullable=False)
    file_hash = Column(String(64), unique=True, index=True) # SHA-256
    file_path = Column(String(512), nullable=False)
    mime_type = Column(String(100))
    file_size = Column(Integer)
    project = Column(String(50))
    category = Column(String(50)) # audios, photos, pdfs, etc.
    metadata_json = Column(Text) # JSON for extra info
    verified = Column(Boolean, default=False)
    uploaded_by = Column(String(36), ForeignKey("usuarios.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

class AgentMessage(Base):
    __tablename__ = "agent_messages"
    id = Column(Integer, primary_key=True)
    sender_agent = Column(String(50), nullable=False) # e.g., 'TPV_ASSISTANT', 'OPENCLAW_DEVOPS'
    receiver_agent = Column(String(50), nullable=False)
    message_type = Column(String(50), default='info') # 'info', 'query', 'task', 'alert'
    content = Column(JSON, nullable=False) 
    status = Column(String(20), default='pending') 
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    processed_at = Column(DateTime)


class PrintJob(Base):
    __tablename__ = "print_jobs"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    payload = Column(Text, nullable=False) # Contenido del ticket (JSON o Texto)
    printer_type = Column(String(50), default="thermal") # thermal, A4, label
    target_device = Column(String(100), nullable=True) # ID del dispositivo destino (Tablet ID o IP)
    status = Column(String(20), default="PENDING") # PENDING, IN_FLIGHT, COMPLETED, FAILED
    error_log = Column(Text, nullable=True)
    attempts = Column(Integer, default=0)
    last_attempt = Column(DateTime, nullable=True)
    metadata_json = Column(JSON, nullable=True) # Datos extra (nº pedido, canal, etc)

    def __repr__(self):
        return f"<PrintJob {self.id} status={self.status}>"
