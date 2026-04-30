import asyncio
import os
import time
from datetime import datetime
from typing import Dict, Any

import psutil
from fastapi import FastAPI, Request
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
from .database import Base, engine
from .routers import admin, auth, hardware, inventory, orders, telemetry, rrhh, webhooks
from .utils.logger import logger
from .utils.exceptions import TPVException, global_exception_handler
from .utils.openapi import custom_openapi
from .services.scheduler import scheduler_loop

# --- Configuración de Control de Tráfico ---
limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="### Sistema TPV de Alto Rendimiento\nEcosistema profesional para la gestión operativa, financiera e inteligente de Carbones y Pollos.",
    docs_url="/docs",
    redoc_url="/redoc",
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
    logger.info(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} Iniciando...")
    Base.metadata.create_all(bind=engine)
    asyncio.create_task(scheduler_loop())

@app.get("/health", tags=["Infraestructura"])
async def health_check() -> Dict[str, Any]:
    try:
        engine.connect().close()
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    mem = psutil.virtual_memory()
    return {
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "telemetry": {
            "database": db_status,
            "cpu_percent": psutil.cpu_percent(),
            "memory_usage": f"{mem.percent}%"
        }
    }

# --- Registro de Routers Modulares ---
app.include_router(auth.router, prefix="/api", tags=["Seguridad"])
app.include_router(orders.router, prefix="/api", tags=["Operaciones"])
app.include_router(inventory.router, prefix="/api", tags=["Logística"])
app.include_router(admin.router, prefix="/api", tags=["Gestión"])
app.include_router(rrhh.router, prefix="/api", tags=["Personal"])
app.include_router(hardware.router, prefix="/api", tags=["Hardware"])
app.include_router(telemetry.router, prefix="/api/system", tags=["Mantenimiento"])
app.include_router(webhooks.router, prefix="/api", tags=["Webhooks"])

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def read_root():
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>TPV Enterprise</h1><p>Interfaz no encontrada.</p>"

@app.get("/sw.js", include_in_schema=False)
async def get_sw():
    return FileResponse("static/sw.js", media_type="application/javascript")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
