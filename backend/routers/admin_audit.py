from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel
import datetime

from ..database import get_db
from ..models import AuditLog, Usuario
from .auth import require_admin
from ..utils.logger import logger

router = APIRouter(prefix="/admin/audit", tags=["Auditoría y Seguridad"])

# --- Esquemas de Datos ---

class AuditLogResponse(BaseModel):
    id: str
    fecha: datetime.datetime
    usuario_id: Optional[str]
    accion: str
    entidad: Optional[str]
    entidad_id: Optional[str]
    ip_origen: Optional[str]
    
    class Config:
        from_attributes = True

# --- Endpoints ---

@router.get("/logs", response_model=List[AuditLogResponse])
async def get_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    admin_user: Usuario = Depends(require_admin)
):
    """
    Recupera el historial de auditoría del sistema.
    Solo accesible por usuarios con rol ADMIN.
    """
    logs = db.query(AuditLog).order_by(desc(AuditLog.fecha)).offset(offset).limit(limit).all()
    return logs

# --- Función Helper para Inserción ---
def log_audit_action(
    db: Session, 
    usuario_id: Optional[str], 
    accion: str, 
    entidad: Optional[str] = None, 
    entidad_id: Optional[str] = None,
    ip_origen: Optional[str] = None,
    payload_previo: Optional[str] = None,
    payload_nuevo: Optional[str] = None
):
    """
    Función helper para registrar una acción en el AuditLog.
    Debe llamarse desde otros endpoints cuando se realice una acción crítica.
    """
    try:
        nuevo_log = AuditLog(
            usuario_id=usuario_id,
            accion=accion,
            entidad=entidad,
            entidad_id=entidad_id,
            ip_origen=ip_origen,
            payload_previo=payload_previo,
            payload_nuevo=payload_nuevo
        )
        db.add(nuevo_log)
        db.commit()
    except Exception as e:
        logger.error(f"Fallo al escribir en AuditLog: {e}")
        db.rollback()
