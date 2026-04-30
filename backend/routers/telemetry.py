from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import LogOperativo
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/telemetry", tags=["Telemetría y Diagnóstico"])

class LogSchema(BaseModel):
    id: str
    modulo: str
    nivel: str
    mensaje: str
    detalles: str = None
    fecha: datetime

    class Config:
        from_attributes = True

@router.get("/logs", response_model=List[LogSchema])
def get_system_logs(limit: int = 50, db: Session = Depends(get_db)):
    """Retorna los últimos N logs operativos del sistema."""
    logs = db.query(LogOperativo).order_by(LogOperativo.fecha.desc()).limit(limit).all()
    return logs

@router.get("/stats")
def get_system_stats():
    """Métricas básicas de hardware (Uso de CPU, RAM, etc)."""
    import psutil
    return {
        "cpu": psutil.cpu_percent(),
        "memory": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage('/').percent
    }
