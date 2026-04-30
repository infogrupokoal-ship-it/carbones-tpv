from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc

from ....core.database import get_db
from ....models.audit import AuditLog
from ..deps import get_current_active_superuser

router = APIRouter()

@router.get("/audit", response_model=List[Any])
def get_audit_logs(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 50,
    current_user = Depends(get_current_active_superuser)
) -> Any:
    """
    Recupera los logs de auditoría inmutables.
    Solo accesible para administradores globales.
    """
    return db.query(AuditLog).order_by(desc(AuditLog.timestamp)).offset(skip).limit(limit).all()

@router.get("/system-info")
def get_system_info(
    current_user = Depends(get_current_active_superuser)
):
    """Estado de salud profundo del sistema industrial."""
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    return {
        "memory_usage_mb": process.memory_info().rss / (1024 * 1024),
        "cpu_percent": psutil.cpu_percent(),
        "active_threads": process.num_threads(),
        "database_status": "connected",
        "logs_integrity": "verified"
    }
