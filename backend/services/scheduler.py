import time
import asyncio
import datetime
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import Pedido, LogOperativo
from ..utils.logger import logger
from ..utils.db_logger import DBLogger
from .financials import FinancialService
import os

async def clean_old_logs():
    """Elimina logs operativos de más de 30 días para ahorrar espacio."""
    db = SessionLocal()
    try:
        limite = datetime.datetime.now() - datetime.timedelta(days=30)
        num_deleted = db.query(LogOperativo).filter(LogOperativo.fecha < limite).delete()
        db.commit()
        if num_deleted > 0:
            logger.info(f"MANTENIMIENTO: Se han purgado {num_deleted} registros de logs antiguos.")
    except Exception as e:
        logger.error(f"ERROR MANTENIMIENTO: {str(e)}")
    finally:
        db.close()

async def generate_auto_z_close():
    """Genera el Cierre Z automáticamente al final de la jornada (03:00 AM)."""
    db = SessionLocal()
    try:
        # Usamos el servicio financiero profesional para el cierre
        resumen = FinancialService.generate_z_report(db, efectivo_declarado=None)
        DBLogger.info("SCHEDULER", f"Cierre Z Automático ejecutado: {resumen[:50]}...")
    except Exception as e:
        DBLogger.error("SCHEDULER", "Fallo en el Cierre Z Automático", e)
    finally:
        db.close()

async def scheduler_loop():
    """Bucle principal de tareas programadas en segundo plano."""
    logger.info("INICIANDO SCHEDULER: Tareas de fondo activas.")
    while True:
        now = datetime.datetime.now()
        
        # Ejecutar mantenimiento a las 03:00 AM
        if now.hour == 3 and now.minute == 0:
            await clean_old_logs()
            await generate_auto_z_close()
            await asyncio.sleep(61) # Evitar re-ejecución en el mismo minuto
            
        # Tarea cada 10 minutos: Sincronización de stock crítica
        if now.minute % 10 == 0 and now.second == 0:
            # Lógica de sync con nube si fuera necesario
            pass
            
        await asyncio.sleep(1)
