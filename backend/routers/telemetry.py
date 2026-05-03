from fastapi import APIRouter
import random
from datetime import datetime, UTC
from fastapi import Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.services.ai_bi_engine import AIBIEngine
from .dependencies import require_admin
from backend.models import Usuario

router = APIRouter(prefix="/telemetry", tags=["Hardware Telemetry & Digital Twin"])

@router.get("/global-nodes")
def get_global_nodes_status(current_user: Usuario = Depends(require_admin)):
    """
    Simula el estado de todos los nodos de hardware en el ecosistema Singularity.
    Esto alimenta la visualizacion del Digital Twin.
    """
    nodes = [
        {"id": "KIOSKO-01", "type": "TABLET", "status": "ONLINE", "load": 45, "temp": 38.5},
        {"id": "KIOSKO-02", "type": "TABLET", "status": "ONLINE", "load": 12, "temp": 36.2},
        {"id": "PRINTER-CASHIER", "type": "PRINTER", "status": "ONLINE", "paper": 85, "temp": 28.1},
        {"id": "PRINTER-KITCHEN", "type": "PRINTER", "status": "ONLINE", "paper": 40, "temp": 32.5},
        {"id": "OVEN-MASTER", "type": "IOT_OVEN", "status": "ACTIVE", "load": 92, "temp": 210.0},
        {"id": "FRYER-01", "type": "IOT_FRYER", "status": "ACTIVE", "load": 65, "temp": 185.5},
        {"id": "REPARTIDOR-01", "type": "MOBILE_NODE", "status": "IN_TRANSIT", "battery": 78, "gps": {"lat": 37.38, "lon": -5.98}},
        {"id": "REPARTIDOR-02", "type": "MOBILE_NODE", "status": "IDLE", "battery": 92, "gps": {"lat": 37.39, "lon": -5.99}}
    ]
    
    # Añadir ruido aleatorio para realismo
    for node in nodes:
        if "load" in node:
            node["load"] += random.randint(-5, 5)
        if "temp" in node:
            node["temp"] += random.uniform(-0.5, 0.5)
        
    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "total_nodes": len(nodes),
        "active_nodes": len([n for n in nodes if n["status"] != "OFFLINE"]),
        "nodes": nodes
    }

@router.get("/logs")
def get_system_logs(current_user: Usuario = Depends(require_admin)):
    """
    Recupera las últimas líneas de los logs del sistema para diagnóstico remoto.
    Reservado para auditoría industrial.
    """
    import os
    log_paths = ["logs/tpv_system.log", "logs/critical_errors.log"]
    logs_data = {}
    
    for path in log_paths:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                # Leer las últimas 100 líneas
                lines = f.readlines()[-100:]
                logs_data[path] = lines
        else:
            logs_data[path] = [f"Log file {path} not found."]
            
    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "logs": logs_data
    }

@router.get("/system-load")
def get_system_load(current_user: Usuario = Depends(require_admin)):
    """Métricas de carga del servidor para el Dashboard Enterprise."""
    import psutil
    import os
    
    return {
        "cpu_usage_pct": psutil.cpu_percent(),
        "memory_usage_pct": psutil.virtual_memory().percent,
        "disk_usage_pct": psutil.disk_usage('/').percent,
        "active_threads": psutil.Process(os.getpid()).num_threads(),
        "uptime_sec": int(datetime.now(UTC).timestamp() - psutil.boot_time()) if hasattr(psutil, "boot_time") else 0
    }

@router.get("/advanced")
def get_advanced_telemetry(current_user: Usuario = Depends(require_admin)):
    """
    Detailed hardware-level profiling for UEOS Singularity Matrix.
    Provides per-core metrics and IO pressure.
    """
    import psutil
    import os
    
    vm = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    net = psutil.net_io_counters()
    proc = psutil.Process(os.getpid())
    
    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "cpu": {
            "overall": psutil.cpu_percent(interval=0.1),
            "per_core": psutil.cpu_percent(percpu=True),
            "count": psutil.cpu_count(),
            "freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
        },
        "memory": {
            "total": vm.total,
            "available": vm.available,
            "percent": vm.percent,
            "process_rss": proc.memory_info().rss,
            "process_vms": proc.memory_info().vms
        },
        "storage": {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": disk.percent
        },
        "network": {
            "bytes_sent": net.bytes_sent,
            "bytes_recv": net.bytes_recv,
            "packets_sent": net.packets_sent,
            "packets_recv": net.packets_recv
        },
        "process": {
            "pid": os.getpid(),
            "threads": proc.num_threads(),
            "create_time": proc.create_time(),
            "status": proc.status()
        }
    }

@router.get("/insights")
def get_proactive_insights(db: Session = Depends(get_db), current_user: Usuario = Depends(require_admin)):
    """
    Recupera 'Neural Insights' generados por la IA proactiva.
    Alimenta las notificaciones inteligentes del Dashboard.
    """
    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "insights": AIBIEngine.get_proactive_insights(db),
        "system_health": AIBIEngine.generate_system_health()
    }
