import asyncio
import datetime
from ..database import SessionLocal
from ..models import LogOperativo
from ..utils.logger import logger
from ..services.reporting import ReportingService

async def clean_old_logs():
    """
    Higienización de Base de Datos: Elimina logs operativos con antigüedad superior 
    a 30 días para mantener el rendimiento y optimizar el almacenamiento.
    """
    db = SessionLocal()
    try:
        limite = datetime.datetime.now() - datetime.timedelta(days=30)
        num_deleted = db.query(LogOperativo).filter(LogOperativo.fecha < limite).delete()
        db.commit()
        if num_deleted > 0:
            logger.info(f"MANTENIMIENTO: Purga de auditoría completada ({num_deleted} registros eliminados).")
    except Exception as e:
        logger.error(f"FALLO EN MANTENIMIENTO DE LOGS: {str(e)}")
    finally:
        db.close()

async def generate_auto_z_close():
    """
    Cierre Autónomo de Jornada: Ejecuta el protocolo de Cierre Z a las 03:00 AM 
    de forma desatendida si el personal olvidó realizarlo manualmente.
    """
    db = SessionLocal()
    try:
        # Ejecutamos el cierre profesional (efectivo_declarado=None indica cierre automático)
        reporte = ReportingService.generar_cierre_z(db, efectivo_declarado=None)
        logger.info(f"SCHEDULER: Cierre Z Automático procesado (ID: {reporte.id})")
    except Exception as e:
        logger.error(f"SCHEDULER: Error crítico en Cierre Z Automático: {str(e)}")
    finally:
        db.close()

async def scheduler_loop():
    """
    Motor de Tareas Programadas: Orquestador de procesos en segundo plano
    para mantenimiento preventivo y consolidación de datos.
    """
    logger.info("SYSTEM: Motor de tareas programadas (Scheduler) activo.")
    
    while True:
        now = datetime.datetime.now()
        
        # Ventana de mantenimiento nocturno (03:00 AM)
        if now.hour == 3 and now.minute == 0:
            await clean_old_logs()
            await generate_auto_z_close()
            # Dormimos el tiempo suficiente para no repetir la ejecución en el mismo minuto
            await asyncio.sleep(65)
            
        # Monitoreo de latencia de bucle (1 segundo)
        await asyncio.sleep(1)
