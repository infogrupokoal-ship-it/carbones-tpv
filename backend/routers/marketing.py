from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.models import WhatsAppTemplate, AuditLog
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
import uuid
import qrcode
import io
import base64

router = APIRouter(prefix="/marketing", tags=["Marketing & Growth Enterprise"])

# --- ESQUEMAS ---

class TemplateCreate(BaseModel):
    nombre: str
    contenido: str
    categoria: str # COMERCIAL, RECORDATORIO, ALERTA, RECUPERACION_CARRITO

class TemplateOut(TemplateCreate):
    id: str
    creado_en: datetime
    model_config = ConfigDict(from_attributes=True)

class CuponCreate(BaseModel):
    codigo: str = Field(..., max_length=15, description="Código del cupón (ej: VERANO20)")
    descuento_porcentaje: float = Field(0.0, description="Porcentaje de descuento")
    descuento_fijo: float = Field(0.0, description="Descuento monetario fijo")
    limite_usos: int = Field(100, description="Cantidad máxima de usos totales")
    valido_hasta: datetime

class CupOut(CuponCreate):
    id: str
    usos_actuales: int
    activo: bool

# --- RUTAS DE TEMPLATES (WHATSAPP) ---

@router.get("/templates", response_model=List[TemplateOut])
def get_templates(db: Session = Depends(get_db)):
    """Obtiene la biblioteca de plantillas de comunicación omnicanal."""
    return db.query(WhatsAppTemplate).all()

@router.post("/templates", response_model=TemplateOut)
def create_template(template: TemplateCreate, db: Session = Depends(get_db)):
    """Crea una nueva plantilla de mensajería para campañas de Growth."""
    nuevo = WhatsAppTemplate(
        id=str(uuid.uuid4()),
        nombre=template.nombre,
        contenido=template.contenido,
        categoria=template.categoria
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.post("/send-bulk")
def send_bulk(template_id: str, client_ids: List[str], db: Session = Depends(get_db)):
    """Motor de envío masivo de campañas de retención y cross-selling."""
    template = db.query(WhatsAppTemplate).filter(WhatsAppTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Plantilla no encontrada")
    
    # En un entorno real se delegaría a RabbitMQ/Celery
    audit = AuditLog(
        id=str(uuid.uuid4()),
        usuario="SYSTEM_MARKETING",
        accion="ENVIO_MASIVO_MARKETING",
        detalle=f"Campaña '{template.nombre}' disparada a {len(client_ids)} clientes objetivo."
    )
    db.add(audit)
    db.commit()
    
    return {
        "status": "success", 
        "message": f"Campaña enviada a la cola de mensajería ({len(client_ids)} destinatarios).",
        "tasa_apertura_estimada": "68%"
    }

# --- RUTAS DE PROMOCIONES Y CUPONES ---

# Simulación de tabla de cupones en memoria por simplicidad estructural 
# (En producción iría a models.py)
CUPONES_DB = []

@router.post("/cupones", response_model=CupOut)
def crear_cupon(cup: CuponCreate):
    """Genera cupones de descuento condicionales para estrategias de adquisición."""
    nuevo_cup = CupOut(
        id=str(uuid.uuid4()),
        usos_actuales=0,
        activo=True,
        **cup.dict()
    )
    CUPONES_DB.append(nuevo_cup)
    return nuevo_cup

@router.get("/cupones", response_model=List[CupOut])
def listar_cupones():
    """Listado del rendimiento de las campañas promocionales activas e inactivas."""
    return CUPONES_DB

@router.get("/qr-promo/{codigo}")
def generar_qr_promocional(codigo: str):
    """
    Motor de Generación QR: Crea dinámicamente un código QR para un cupón o campaña.
    El cliente escanea esto en su mesa o flyer para reclamar el premio.
    """
    qr_data = f"https://kiosko.carbonesypollos.com/promo?code={codigo}"
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="#FF5722", back_color="white")
    
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    qr_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    
    return {
        "status": "success",
        "codigo": codigo,
        "qr_base64": f"data:image/png;base64,{qr_base64}",
        "url_destino": qr_data
    }
