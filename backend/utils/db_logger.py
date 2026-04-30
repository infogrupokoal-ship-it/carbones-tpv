import json
import traceback
from datetime import datetime
from sqlalchemy.orm import Session
from ..models import LogOperativo
from ..database import SessionLocal

class DBLogger:
    @staticmethod
    def log(modulo: str, nivel: str, mensaje: str, detalles: str = None):
        """
        Registra un evento técnico en la base de datos para auditoría persistente.
        Diseñado para procesos en segundo plano (Scheduler, Sync, AI).
        """
        db = SessionLocal()
        try:
            nuevo_log = LogOperativo(
                modulo=modulo,
                nivel=nivel,
                mensaje=mensaje,
                detalles=detalles,
                fecha=datetime.now()
            )
            db.add(nuevo_log)
            db.commit()
        except Exception as e:
            print(f"CRITICAL: Fallo al escribir log en DB: {e}")
        finally:
            db.close()

    @staticmethod
    def error(modulo: str, mensaje: str, exception: Exception = None):
        """Atajo para registrar errores con traceback completo."""
        detalles = traceback.format_exc() if exception else None
        DBLogger.log(modulo, "ERROR", mensaje, detalles)

    @staticmethod
    def info(modulo: str, mensaje: str):
        """Atajo para registros informativos."""
        DBLogger.log(modulo, "INFO", mensaje)
