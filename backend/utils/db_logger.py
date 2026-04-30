import datetime
from ..database import SessionLocal
from ..models import LogOperativo
import logging

logger = logging.getLogger("TPV-Enterprise")

class DBLogger:
    @staticmethod
    def log(level: str, module: str, message: str, details: str = None):
        """Persiste un log directamente en la base de datos para auditoría legal."""
        db = SessionLocal()
        try:
            nuevo_log = LogOperativo(
                fecha=datetime.datetime.now(),
                nivel=level,
                modulo=module,
                mensaje=message,
                detalles=details
            )
            db.add(nuevo_log)
            db.commit()
            
            # También logueamos a consola/archivo
            log_msg = f"[{module}] {message}"
            if level == "INFO":
                logger.info(log_msg)
            elif level == "WARN":
                logger.warning(log_msg)
            elif level == "ERR":
                logger.error(log_msg)
            
        except Exception as e:
            logger.error(f"FALLO CRÍTICO EN DBLogger: {str(e)}")
        finally:
            db.close()

    @staticmethod
    def info(module: str, message: str, details: str = None):
        DBLogger.log("INFO", module, message, details)

    @staticmethod
    def error(module: str, message: str, error: Exception = None):
        details = str(error) if error else None
        DBLogger.log("ERR", module, message, details)
