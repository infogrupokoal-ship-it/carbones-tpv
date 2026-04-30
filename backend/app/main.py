import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .core.config import settings
from .api.v1.api import api_router
from .core.database import engine, Base

# Configuración de Logs Industrial
if not os.path.exists(settings.LOGS_DIR):
    os.makedirs(settings.LOGS_DIR)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(settings.LOGS_DIR, "tpv_enterprise.log")),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Asegurar directorios de persistencia
if not os.path.exists(settings.INSTANCE_DIR):
    os.makedirs(settings.INSTANCE_DIR)

# Inicialización de DB (Auto-migración simple para v4.0)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Backend Industrial para Gestión de Hostelería"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rutas de API
app.include_router(api_router, prefix=settings.API_V1_STR)

# Servir archivos estáticos (Frontend)
# Nota: En producción esto lo haría Nginx, pero para desarrollo/Render lo servimos aquí.
static_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")

@app.get("/health")
def health_check():
    return {"status": "online", "version": settings.APP_VERSION, "environment": "enterprise"}

@app.get("/")
def root():
    return {"message": "TPV Enterprise API v4.0. Access /static/portal.html for management."}
