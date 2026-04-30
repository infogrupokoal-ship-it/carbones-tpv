import os
import time

import psutil
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db

router = APIRouter()


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """
    Diagnóstico completo del sistema: Base de datos, Hardware y Conectividad.
    Ideal para dashboards de mantenimiento o sistemas de monitoreo externo.
    """
    start_time = time.time()

    # 1. Verificar Base de Datos
    db_status = "DOWN"
    try:
        db.execute(text("SELECT 1"))
        db_status = "UP"
    except Exception as e:
        db_status = f"ERROR: {str(e)}"

    # 2. Métricas del Host (Hardware)
    cpu_usage = psutil.cpu_percent()
    ram_usage = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage("/").percent

    # 3. Estado de Servicios Externos (Simulado/Rápido)
    stripe_configured = bool(settings.STRIPE_SECRET_KEY)
    waha_status = "NOT_CONFIGURED" if not settings.WAHA_URL else "CONFIGURED"

    latency_ms = (time.time() - start_time) * 1000

    return {
        "status": "OPERATIONAL" if db_status == "UP" else "DEGRADED",
        "timestamp": time.time(),
        "latency_ms": round(latency_ms, 2),
        "components": {
            "database": db_status,
            "cpu_percent": cpu_usage,
            "ram_percent": ram_usage,
            "disk_percent": disk_usage,
            "stripe": "READY" if stripe_configured else "MISSING_KEYS",
            "waha": waha_status,
        },
        "version": settings.VERSION,
    }


@router.get("/logs")
def get_recent_logs(lines: int = 100):
    """Permite visualizar los últimos eventos del servidor para depuración rápida."""
    log_path = "instance/server.log"
    if not os.path.exists(log_path):
        return {"error": "Archivo de logs no encontrado"}

    try:
        with open(log_path, "r") as f:
            content = f.readlines()
            return {"logs": content[-lines:]}
    except Exception as e:
        return {"error": str(e)}
