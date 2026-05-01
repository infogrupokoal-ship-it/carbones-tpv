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

async def check_low_stock():
    """
    Monitor de Suministros: Analiza el inventario en tiempo real y genera alertas 
    críticas si algún producto esencial baja de 5 unidades.
    """
    db = SessionLocal()
    try:
        from ..models import Producto
        alertas = db.query(Producto).filter(Producto.stock_actual < 5, Producto.is_active == True).all()
        for p in alertas:
            logger.warning(f"⚠️ ALERTA DE STOCK: {p.nombre} está bajo mínimos ({p.stock_actual} uds).")
            # Podríamos disparar WhatsApp aquí si fuera crítico
    except Exception as e:
        logger.error(f"FALLO EN MONITOR DE STOCK: {str(e)}")
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
    
    iteration = 0
    while True:
        now = datetime.datetime.now()
        
        # Tarea de cada hora: Monitor de Stock
        if iteration % 3600 == 0:
            await check_low_stock()
            logger.info(f"HEARTBEAT: Sistema TPV operativo. Latencia de red: {iteration} ticks.")

        # Ventana de mantenimiento nocturno (03:00 AM)
        if now.hour == 3 and now.minute == 0:
            await clean_old_logs()
            await generate_auto_z_close()
            await asyncio.sleep(65)
            
        iteration += 1
        await asyncio.sleep(1)
