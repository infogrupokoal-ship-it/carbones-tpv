from fastapi import APIRouter
import random
from datetime import datetime

router = APIRouter(prefix="/telemetry", tags=["Hardware Telemetry & Digital Twin"])

@router.get("/global-nodes")
def get_global_nodes_status():
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
        if "load" in node: node["load"] += random.randint(-5, 5)
        if "temp" in node: node["temp"] += random.uniform(-0.5, 0.5)
        
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "total_nodes": len(nodes),
        "active_nodes": len([n for n in nodes if n["status"] != "OFFLINE"]),
        "nodes": nodes
    }

@router.get("/system-load")
def get_system_load():
    """Métricas de carga del servidor para el Dashboard Enterprise."""
    import psutil
    import os
    
    return {
        "cpu_usage_pct": psutil.cpu_percent(),
        "memory_usage_pct": psutil.virtual_memory().percent,
        "disk_usage_pct": psutil.disk_usage('/').percent,
        "active_threads": psutil.Process(os.getpid()).num_threads(),
        "uptime_sec": int(datetime.utcnow().timestamp() - psutil.boot_time()) if hasattr(psutil, "boot_time") else 0
    }

@router.get("/advanced")
def get_advanced_telemetry():
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
        "timestamp": datetime.utcnow().isoformat(),
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
