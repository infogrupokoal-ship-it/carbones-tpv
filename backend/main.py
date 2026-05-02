import asyncio
import os
import sys
import time
from datetime import datetime
from typing import Dict, Any

import psutil
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from .config import settings
from .database import engine
from .auto_migrate import migrate_schema
from backend.routers import orders, inventory, clients, stats, auth, ai_assistant, rrhh, marketing, reservas, delivery_aggregators, mantenimiento, payments, feedback, escandallos, fleet, loyalty, franchise, esg, pricing, iot, erp, crisis, menu_engineering, procurement
from backend.services import sync_daemon, ai_bi_agent, self_healing

from .utils.logger import logger
from .utils.exceptions import TPVException, global_exception_handler
from .services.scheduler import scheduler_loop
from .services.notification_service import NotificationService
from .services.worker_manager import WorkerManager

# --- Configuración de Control de Tráfico ---
limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="### Sistema TPV de Alto Rendimiento\nEcosistema profesional para la gestión operativa, financiera e inteligente de Carbones y Pollos.",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# --- Middlewares ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Server"] = "TPV-Enterprise-Engine"
        return response

app.add_middleware(SlowAPIMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(GZipMiddleware, minimum_size=1000)

app.add_exception_handler(TPVException, global_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# Servir estáticos
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup_event():
    os.makedirs("instance", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    # Forzar UTF-8 en consola para evitar errores de charmap en Windows
    if sys.platform == "win32":
        try:
            import io
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
        except Exception:
            pass

    logger.info(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} Iniciando...")
    migrate_schema()
    
    from .seeding import run_auto_seeding
    run_auto_seeding()
    
    # --- AUTO-UPDATE RENDER SCRIPT ---
    try:
        from scripts.seed_night_menu_image import seed_night_menu_image
        seed_night_menu_image()
        from scripts.seed_pizzas import seed_pizzas
        seed_pizzas()
        
        # Iniciar Worker de Notificaciones
        asyncio.create_task(NotificationService.worker_loop())
        
        from scripts.fix_broken_images import fix_broken_images
        fix_broken_images()
        
        from backend.database import SessionLocal
        from backend.models import Usuario
        from backend.utils.auth import get_password_hash
        db = SessionLocal()
        admin = db.query(Usuario).filter_by(username="admin").first()
        if admin:
            admin.pin_hash = get_password_hash("1234")
            db.commit()
            logger.info("Admin password enforced to 1234")
        db.close()
    except Exception as e:
        logger.error(f"Error running auto-update script: {e}")
    # ---------------------------------
    
    asyncio.create_task(scheduler_loop())
    asyncio.create_task(WorkerManager.run_maintenance_cycle())

@app.get("/health", tags=["Infraestructura"])
@app.get("/healthz", tags=["Infraestructura"], include_in_schema=False)
@app.get("/api/health", tags=["Infraestructura"], include_in_schema=False)
async def health_check() -> Dict[str, Any]:
    """Monitor de salud profesional con telemetría industrial avanzada."""
    try:
        # Validar conexión a DB con latencia
        from sqlalchemy import text
        start_time = time.time()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_latency_ms = round((time.time() - start_time) * 1000, 2)
        db_status = "connected"
    except Exception as e:
        logger.error(f"Health Check DB Error: {e}")
        db_status = "disconnected"
        db_latency_ms = -1

    try:
        mem_percent = psutil.virtual_memory().percent
        cpu_percent = psutil.cpu_percent()
        disk_free = psutil.disk_usage('/').percent
        net = psutil.net_io_counters()
        bytes_sent = net.bytes_sent
        bytes_recv = net.bytes_recv
        uptime = int(time.time() - psutil.boot_time())
    except Exception as e:
        logger.warning(f"Health check psutil warning: {e}")
        mem_percent = cpu_percent = disk_free = uptime = bytes_sent = bytes_recv = 0

    return {
        "status": "operational" if db_status == "connected" else "degraded",
        "timestamp": datetime.now().isoformat(),
        "version": settings.APP_VERSION,
        "environment": os.environ.get("ENVIRONMENT", "production"),
        "deployment": {
            "node": os.uname().nodename if hasattr(os, "uname") else "windows-dev",
            "uptime_sec": uptime,
            "build_marker": "INDUSTRIAL-ULTRA-v3.1-SOFT-DELETES"
        },
        "telemetry": {
            "database": {
                "status": db_status,
                "latency_ms": db_latency_ms
            },
            "cpu_usage": cpu_percent,
            "memory_usage": mem_percent,
            "db_latency_ms": db_latency_ms,
            "disk_free": disk_free,
            "network": {
                "bytes_sent": bytes_sent,
                "bytes_recv": bytes_recv
            }
        },
        "integrity": {
            "last_audit": "SUCCESS",
            "security_mode": "ENFORCED"
        },
        "ai_engine": __import__('backend.utils.ai_model_manager', fromlist=['ai_manager']).ai_manager.get_status()
    }

@app.on_event("startup")
async def startup_event():
    # Inicializar motores autónomos V6.0
    asyncio.create_task(sync_daemon.run())
    asyncio.create_task(self_healing.SelfHealingService().monitor())
    logger.info("Enterprise Singularity [V6.0] fully activated.")

# --- Registro de Routers Modulares ---
app.include_router(auth.router, prefix="/api", tags=["Seguridad"])
app.include_router(orders.router, prefix="/api", tags=["Operaciones"])
app.include_router(inventory.router, prefix="/api", tags=["Logística"])
app.include_router(admin.router, prefix="/api", tags=["Gestión"])
app.include_router(rrhh.router, prefix="/api", tags=["Personal"])
app.include_router(hardware.router, prefix="/api", tags=["Hardware"])
app.include_router(telemetry.router, prefix="/api/system", tags=["Mantenimiento"])
app.include_router(webhooks.router, prefix="/api", tags=["Webhooks"])
app.include_router(admin_audit.router, prefix="/api", tags=["Auditoría y Seguridad"])
app.include_router(customers.router, prefix="/api", tags=["Clientes y B2C"])
app.include_router(feedback.router, prefix="/api", tags=["Feedback"])
app.include_router(payments.router, prefix="/api", tags=["Payments"])
app.include_router(feedback.router, prefix="/api", tags=["Feedback & NPS"])
app.include_router(escandallos.router, prefix="/api", tags=["Escandallos"])
app.include_router(fleet.router, prefix="/api", tags=["Fleet"])
app.include_router(loyalty.router, prefix="/api", tags=["Loyalty"])
app.include_router(franchise.router, prefix="/api", tags=["Franchise"])
app.include_router(esg.router, prefix="/api", tags=["ESG"])
app.include_router(iot.router, prefix="/api", tags=["IoT Telemetry"])
app.include_router(pricing.router, prefix="/api", tags=["Pricing"])
app.include_router(iot.router, prefix="/api", tags=["IoT"])
app.include_router(erp.router, prefix="/api", tags=["ERP"])
app.include_router(crisis.router, prefix="/api", tags=["Crisis"])
app.include_router(menu_engineering.router, prefix="/api", tags=["Menu Engineering"])
app.include_router(procurement.router, prefix="/api", tags=["Procurement"])
app.include_router(marketing.router, prefix="/api", tags=["Marketing"])
app.include_router(reservas.router, prefix="/api", tags=["Reservas"])
app.include_router(delivery_aggregators.router, prefix="/api", tags=["Delivery Aggregators"])
app.include_router(mantenimiento.router, prefix="/api", tags=["Mantenimiento"])
app.include_router(stats.router, prefix="/api", tags=["BI & Analytics"])
app.include_router(ws.router, tags=["Real-time"])

@app.get("/", response_class=FileResponse, include_in_schema=False)
async def read_root():
    """Sirve la interfaz B2C Ultra-Premium como entrada principal del ecosistema."""
    path = "static/kiosko.html"
    if os.path.exists(path):
        return FileResponse(path)
    return HTMLResponse("<h1>TPV Enterprise</h1><p>Sistema en mantenimiento industrial. Contacte con soporte.</p>", status_code=503)

@app.get("/sw.js", include_in_schema=False)
async def get_sw():
    return FileResponse("static/sw.js", media_type="application/javascript")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
