from sqlalchemy.orm import Session
from ..models import AuditLog
import uuid
from datetime import datetime
from typing import Optional

def log_action(
    db: Session, 
    accion: str, 
    entidad: str = "SISTEMA", 
    entidad_id: Optional[str] = None, 
    usuario_id: Optional[str] = None,
    ip_origen: Optional[str] = "127.0.0.1",
    payload_previo: Optional[str] = None,
    payload_nuevo: Optional[str] = None
):
    """
    Registra una acción de auditoría de seguridad y trazabilidad.
    """
    try:
        audit_entry = AuditLog(
            id=str(uuid.uuid4()),
            fecha=datetime.now(datetime.timezone.utc),
            usuario_id=usuario_id,
            accion=accion,
            entidad=entidad,
            entidad_id=entidad_id,
            ip_origen=ip_origen,
            payload_previo=payload_previo,
            payload_nuevo=payload_nuevo
        )
        db.add(audit_entry)
        db.commit()
    except Exception as e:
        db.rollback()
        # En un entorno crítico deberíamos forzar la caída o alertar si la auditoría falla.
        # Por ahora logeamos el error internamente.
        from .logger import logger
        logger.error(f"Error escribiendo AuditLog: {e}")
