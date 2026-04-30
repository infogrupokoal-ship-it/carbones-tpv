import os
import time
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from .core.config import settings
from .core.database import Base, engine
from .api.v1.api import api_router

# Asegurar infraestructura Enterprise
os.makedirs(settings.LOGS_DIR, exist_ok=True)
os.makedirs(settings.INSTANCE_DIR, exist_ok=True)

# Configuración de Logging de Grado Industrial
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s [%(levelname)s] [%(name)s] [%(process)d] %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(settings.LOGS_DIR, "enterprise.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Carbones-Enterprise")

# Inicialización de Base de Datos (Si no se usa Alembic para el primer arranque)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Middlewares de Optimización y Seguridad
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware de Telemetría y Rendimiento
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Montaje de Recursos Estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Registro de Rutas Enterprise (v1)
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health", tags=["Infraestructura"])
def health_check():
    return {
        "status": "online",
        "version": settings.APP_VERSION,
        "environment": "production" if not settings.DEBUG else "development",
        "timestamp": time.time()
    }
