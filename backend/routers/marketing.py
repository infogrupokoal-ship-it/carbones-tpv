from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.models import WhatsAppTemplate, AuditLog
from pydantic import BaseModel
from datetime import datetime
import uuid

router = APIRouter(prefix="/marketing", tags=["Marketing & Growth"])

class TemplateCreate(BaseModel):
    nombre: str
    contenido: str
    categoria: str # COMERCIAL, RECORDATORIO, ALERTA

class TemplateOut(TemplateCreate):
    id: str
    creado_en: datetime
    class Config:
        from_attributes = True

@router.get("/templates", response_model=List[TemplateOut])
def get_templates(db: Session = Depends(get_db)):
    return db.query(WhatsAppTemplate).all()

@router.post("/templates", response_model=TemplateOut)
def create_template(template: TemplateCreate, db: Session = Depends(get_db)):
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
    # Simulación de envío masivo
    template = db.query(WhatsAppTemplate).filter(WhatsAppTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Plantilla no encontrada")
    
    # Registrar en auditoría
    audit = AuditLog(
        id=str(uuid.uuid4()),
        usuario="SISTEMA",
        accion="ENVIO_MASIVO_MARKETING",
        detalle=f"Enviado template {template.nombre} a {len(client_ids)} clientes."
    )
    db.add(audit)
    db.commit()
    
    return {"status": "success", "sent": len(client_ids)}
