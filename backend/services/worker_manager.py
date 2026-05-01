import asyncio
import os
import shutil
import time
from datetime import datetime, timedelta
from backend.utils.logger import logger
from backend.database import SessionLocal
from backend.models import AuditLog

class WorkerManager:
    """
    Gestor autónomo de tareas de fondo para mantenimiento industrial.
    Misión: Garantizar la estabilidad 24/7 y la integridad de datos.
    """
    
    @staticmethod
    async def cleanup_old_logs(days=30):
        """Elimina logs de auditoría antiguos para optimizar la base de datos."""
        logger.info(f"🧹 Iniciando limpieza de logs de auditoría (> {days} días)...")
        db = SessionLocal()
        try:
            threshold = datetime.now() - timedelta(days=days)
            deleted = db.query(AuditLog).filter(AuditLog.timestamp < threshold).delete()
            db.commit()
            logger.info(f"✅ Se han eliminado {deleted} entradas de auditoría antiguas.")
        except Exception as e:
            logger.error(f"❌ Error en limpieza de logs: {e}")
            db.rollback()
        finally:
            db.close()

    @staticmethod
    async def auto_backup_db():
        """Crea una copia de seguridad de la base de datos sqlite."""
        logger.info("💾 Iniciando Backup automático de la base de datos...")
        src = "instance/tpv.db"
        if not os.path.exists(src):
            logger.warning("⚠️ No se encontró la DB en instance/tpv.db")
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs("backups", exist_ok=True)
        dst = f"backups/tpv_backup_{timestamp}.db"
        
        try:
            shutil.copy2(src, dst)
            logger.info(f"✅ Backup creado con éxito: {dst}")
            
            # Limpiar backups antiguos (mantener solo los últimos 5)
            backups = sorted([os.path.join("backups", f) for f in os.listdir("backups") if f.endswith(".db")])
            if len(backups) > 5:
                for b in backups[:-5]:
                    os.remove(b)
                    logger.info(f"🗑️ Backup antiguo eliminado: {b}")
        except Exception as e:
            logger.error(f"❌ Error en backup: {e}")

    @classmethod
    async def run_maintenance_cycle(cls):
        """Ciclo principal del worker de mantenimiento."""
        while True:
            try:
                # Ejecutar tareas una vez al día (cada 24h)
                await cls.cleanup_old_logs()
                await cls.auto_backup_db()
                
                # Dormir 24 horas
                logger.info("💤 Tareas de mantenimiento completadas. Próximo ciclo en 24h.")
                await asyncio.sleep(86400) 
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Error crítico en ciclo de mantenimiento: {e}")
                await asyncio.sleep(3600) # Reintentar en 1h si hay error
