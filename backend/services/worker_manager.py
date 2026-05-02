import asyncio
import os
import shutil
from datetime import datetime, timedelta
from backend.utils.logger import logger
from backend.database import SessionLocal
from backend.models import AuditLog

class WorkerManager:
    """
    Gestor autonomo de tareas de fondo para mantenimiento industrial.
    Mision: Garantizar la estabilidad 24/7 y la integridad de datos.
    """
    
    @classmethod
    async def cleanup_old_logs(cls, days=30):
        """Elimina logs de auditoria antiguos para optimizar la base de datos."""
        logger.info(f"WORKER: Iniciando limpieza de logs de auditoria (> {days} dias)...")
        db = SessionLocal()
        try:
            threshold = datetime.now() - timedelta(days=days)
            # Aseguramos el uso de 'fecha' segun el modelo definido en models.py
            deleted = db.query(AuditLog).filter(AuditLog.fecha < threshold).delete()
            db.commit()
            logger.info(f"WORKER: Limpieza completada. {deleted} entradas eliminadas.")
        except Exception as e:
            logger.error(f"WORKER ERROR: Limpieza de logs fallida: {e}")
            db.rollback()
        finally:
            db.close()

    @classmethod
    async def auto_backup_db(cls):
        """Crea una copia de seguridad de la base de datos sqlite."""
        logger.info("WORKER: Iniciando Backup automatico...")
        src = "tpv_data.sqlite"
        if not os.path.exists(src):
            logger.warning("WORKER WARN: No se encontro la DB en tpv_data.sqlite")
            return
            
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs("backups", exist_ok=True)
        dst = f"backups/tpv_backup_{timestamp_str}.sqlite"
        
        try:
            shutil.copy2(src, dst)
            logger.info(f"WORKER: Backup creado exitosamente en {dst}")
            
            # Limpiar backups antiguos (mantener solo los ultimos 5)
            backups = sorted([os.path.join("backups", f) for f in os.listdir("backups") if f.endswith(".sqlite")])
            if len(backups) > 5:
                for b in backups[:-5]:
                    os.remove(b)
                    logger.info(f"WORKER: Backup antiguo eliminado: {b}")
        except Exception as e:
            logger.error(f"WORKER ERROR: Backup fallido: {e}")

    @classmethod
    async def run_maintenance_cycle(cls):
        """Ciclo principal del worker de mantenimiento."""
        logger.info("WORKER: Ciclo de mantenimiento activado.")
        while True:
            try:
                # Ejecutar tareas
                await cls.cleanup_old_logs()
                await cls.auto_backup_db()
                
                logger.info("WORKER: Tareas completadas. Proximo ciclo en 24h.")
                await asyncio.sleep(86400) 
            except asyncio.CancelledError:
                logger.info("WORKER: Ciclo cancelado.")
                break
            except Exception as e:
                logger.error(f"WORKER CRITICAL: Error en ciclo: {e}")
                await asyncio.sleep(3600) # Reintentar en 1h
