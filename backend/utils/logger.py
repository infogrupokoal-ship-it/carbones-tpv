import logging
import sys
from logging.handlers import RotatingFileHandler
import os

# Asegurar que el directorio de logs existe
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Configuración de formato profesional
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Crear el logger principal
logger = logging.getLogger("TPV_ENTERPRISE")
logger.setLevel(logging.INFO)

# Handler para consola (Standard Output) con soporte robusto de codificación
if sys.platform == "win32":
    # En Windows, intentamos forzar UTF-8 para la consola si es posible
    import io
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except (AttributeError, io.UnsupportedOperation):
        pass

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
logger.addHandler(console_handler)

# Handler para archivo con rotación (10MB por archivo, máx 5 archivos)
file_handler = RotatingFileHandler(
    os.path.join(LOG_DIR, "tpv_system.log"),
    maxBytes=10*1024*1024,
    backupCount=5,
    encoding="utf-8"
)
file_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
logger.addHandler(file_handler)

# Logger específico para errores críticos
error_file_handler = RotatingFileHandler(
    os.path.join(LOG_DIR, "critical_errors.log"),
    maxBytes=5*1024*1024,
    backupCount=3,
    encoding="utf-8"
)
error_file_handler.setLevel(logging.ERROR)
error_file_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
logger.addHandler(error_file_handler)
