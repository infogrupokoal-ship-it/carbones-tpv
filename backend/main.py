import asyncio
import logging
import os
import time
import psutil
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from starlette.middleware.base import BaseHTTPMiddleware

from .config import settings
from .database import Base, engine
from .routers import admin, auth, hardware, inventory, orders, telemetry, rrhh
from .utils.logger import logger
from .utils.exceptions import TPVException, global_exception_handler
from .utils.openapi import custom_openapi
from .services.scheduler import scheduler_loop

# Configuración de logs profesional
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    handlers=[logging.FileHandler("instance/server.log"), logging.StreamHandler()],
)
logger = logging.getLogger("TPV-Enterprise")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="### Sistema TPV de Alto Rendimiento\nEcosistema profesional para la gestión operativa, financiera e inteligente de Carbones y Pollos.",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "Soporte Técnico Koal",
        "url": "https://grupokoal.com",
        "email": "soporte@grupokoal.com",
    },
    license_info={
        "name": "Propiedad Privada - Carbones y Pollos",
    },
)

# --- Middlewares de Seguridad Enterprise ---
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
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["X-Robots-Tag"] = "noindex, nofollow"
        response.headers["Server"] = "TPV-Enterprise-Engine"
        return response

app.add_middleware(SecurityHeadersMiddleware)

@app.middleware("http")
async def performance_telemetry_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f}s"
    
    log_msg = f"{request.method} {request.url.path} - {response.status_code} ({process_time:.4f}s)"
    if process_time > 2.0:
        logger.warning(f"⚠️ PETICIÓN CRÍTICA LENTA: {log_msg}")
    elif response.status_code >= 400:
        logger.error(f"❌ FALLO DE CLIENTE/SERVIDOR: {log_msg}")
    else:
        logger.info(log_msg)
        
    return response

app.add_middleware(GZipMiddleware, minimum_size=1000)

# --- Manejo de Errores Global ---
app.add_exception_handler(TPVException, global_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# Servir estáticos si existen
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup_event():
    logger.info(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} Iniciando...")
    # Asignar esquema personalizado
    app.openapi = lambda: custom_openapi(app)
    Base.metadata.create_all(bind=engine)
    asyncio.create_task(scheduler_loop())
    logger.info("✅ Motor de tareas (Scheduler) sincronizado.")

@app.get("/health", tags=["Infraestructura"])
async def health_check() -> Dict[str, Any]:
    """
    Monitor de salud industrial del sistema.
    Retorna métricas de hardware, base de datos y uptime.
    """
    try:
        # Test simple de DB
        engine.connect().close()
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')

    return {
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "version": settings.APP_VERSION,
        "environment": "production" if not settings.DEBUG else "development",
        "telemetry": {
            "database": db_status,
            "cpu_percent": psutil.cpu_percent(),
            "memory_usage": f"{mem.percent}%",
            "disk_free_gb": f"{disk.free / (1024**3):.2f}"
        }
    }

# --- Registro de Routers Modulares (API Profesional) ---
app.include_router(auth.router, prefix="/api", tags=["Seguridad"])
app.include_router(orders.router, prefix="/api", tags=["Operaciones"])
app.include_router(inventory.router, prefix="/api", tags=["Logística"])
app.include_router(admin.router, prefix="/api", tags=["Gestión"])
app.include_router(rrhh.router, prefix="/api", tags=["Personal"])
app.include_router(hardware.router, prefix="/api", tags=["Hardware"])
app.include_router(telemetry.router, prefix="/api/system", tags=["Mantenimiento"])

# Routers de compatibilidad (Legacy)
app.include_router(orders.router_legacy, prefix="/api", include_in_schema=False)
app.include_router(inventory.router_legacy, prefix="/api", include_in_schema=False)
app.include_router(inventory.router_productos, prefix="/api", include_in_schema=False)
app.include_router(admin.router_legacy, prefix="/api", include_in_schema=False)

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def read_root():
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"<h1>{settings.APP_NAME}</h1><p>Interfaz no encontrada.</p>"

@app.get("/sw.js", include_in_schema=False)
async def get_sw():
    return FileResponse("static/sw.js", media_type="application/javascript")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
