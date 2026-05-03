from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel
import datetime
import uuid

from ..database import get_db
from ..models import AuditLog
# from .auth import require_admin  <-- Movido a los endpoints para evitar circular import

from ..utils.logger import logger

router = APIRouter(prefix="/admin/audit", tags=["Auditoría y Seguridad"])

# --- Esquemas de Datos ---

class AuditLogResponse(BaseModel):
    id: str
    timestamp: datetime.datetime
    user_id: Optional[str]
    action: str
    resource: Optional[str]
    resource_id: Optional[str]
    ip_address: Optional[str]
    details: Optional[str]
    
    class Config:
        from_attributes = True

# --- Endpoints ---

@router.get("/logs", response_model=List[AuditLogResponse])
async def get_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    # Importación diferida para evitar circular import
    admin_user = Depends(__import__('backend.routers.auth', fromlist=['require_admin']).require_admin)

):
    """
    Recupera el historial de auditoría del sistema.
    Solo accesible por usuarios con rol ADMIN.
    """
    logs = db.query(AuditLog).order_by(desc(AuditLog.timestamp)).offset(offset).limit(limit).all()
    return logs

@router.get("/export/csv")
async def export_audit_csv(
    db: Session = Depends(get_db),
    # Importación diferida
    admin_user = Depends(__import__('backend.routers.auth', fromlist=['require_admin']).require_admin)

):
    """Genera un reporte CSV de la auditoría para cumplimiento legal."""
    import csv
    import io
    from fastapi.responses import StreamingResponse

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "TIMESTAMP", "USER_ID", "ACTION", "RESOURCE", "RESOURCE_ID", "IP", "DETAILS"])
    
    logs = db.query(AuditLog).order_by(desc(AuditLog.timestamp)).all()
    for log in logs:
        writer.writerow([
            log.id, 
            log.timestamp.isoformat(), 
            log.user_id or "SISTEMA",
            log.action,
            log.resource,
            log.resource_id,
            log.ip_address,
            log.details
        ])
    
    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=audit_log_carbones.csv"}
    )

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
    Traduce los parámetros a los campos del modelo actual.
    """
    try:
        import json
        details_dict = {}
        if payload_previo:
            details_dict["prev"] = payload_previo
        if payload_nuevo:
            details_dict["new"] = payload_nuevo
        
        nuevo_log = AuditLog(
            id=str(uuid.uuid4()),
            user_id=usuario_id,
            action=accion,
            resource=entidad,
            resource_id=entidad_id,
            ip_address=ip_origen,
            details=json.dumps(details_dict) if details_dict else None,
            timestamp=datetime.datetime.utcnow()
        )
        db.add(nuevo_log)
        db.commit()
    except Exception as e:
        logger.error(f"Fallo al escribir en AuditLog: {e}")
        db.rollback()
