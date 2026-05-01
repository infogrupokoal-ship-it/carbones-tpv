from fastapi import APIRouter, Depends, HTTPException
import psutil
import os
import platform
import time
from datetime import datetime
from backend.auth import get_current_user

router = APIRouter(prefix="/api/telemetry", tags=["telemetry"])

# Iniciar contador de tiempo
START_TIME = time.time()

@router.get("/status")
async def get_system_status(current_user: dict = Depends(get_current_user)):
    """
    Retorna telemetría avanzada del servidor para el dashboard administrativo.
    Requiere permisos de administrador.
    """
    if current_user.get("rol") != "ADMIN":
        raise HTTPException(status_code=403, detail="Acceso denegado")

    uptime = str(datetime.fromtimestamp(START_TIME))
    process = psutil.Process(os.getpid())
    
    return {
        "os": platform.system(),
        "node": platform.node(),
        "release": platform.release(),
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory": {
            "total": psutil.virtual_memory().total,
            "available": psutil.virtual_memory().available,
            "percent": psutil.virtual_memory().percent,
            "used": psutil.virtual_memory().used
        },
        "disk": psutil.disk_usage('/')._asdict(),
        "process": {
            "memory_info": process.memory_info()._asdict(),
            "cpu_percent": process.cpu_percent(),
            "threads": process.num_threads(),
            "uptime_seconds": int(time.time() - START_TIME)
        },
        "timestamp": datetime.now().isoformat()
    }

@router.get("/health")
async def health_check():
    """Endpoint público para monitorización (Render/UptimeRobot)"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}
