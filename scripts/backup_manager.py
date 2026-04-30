import shutil
import datetime
import os
import glob
from backend.config import settings
from backend.utils.logger import logger

class BackupManager:
    """Gestor profesional de backups y mantenimiento de datos."""
    
    BACKUP_DIR = "instance/backups"
    MAX_BACKUPS = 30 # Retener 1 mes de backups diarios
    
    @classmethod
    def execute_backup(cls):
        """Realiza un backup en caliente de la base de datos operativa."""
        if not os.path.exists(cls.BACKUP_DIR):
            os.makedirs(cls.BACKUP_DIR)
            
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        source = "tpv_data.sqlite"
        destination = os.path.join(cls.BACKUP_DIR, f"tpv_backup_{timestamp}.sqlite")
        
        try:
            if os.path.exists(source):
                shutil.copy2(source, destination)
                logger.info(f"💾 Backup completado: {destination}")
                cls.prune_old_backups()
                return True
            else:
                logger.error("❌ Error: No se encontró el archivo de base de datos para backup.")
                return False
        except Exception as e:
            logger.error(f"❌ Fallo crítico en el backup: {e}")
            return False

    @classmethod
    def prune_old_backups(cls):
        """Elimina backups antiguos para ahorrar espacio en disco."""
        files = glob.glob(os.path.join(cls.BACKUP_DIR, "*.sqlite"))
        files.sort(key=os.path.getmtime)
        
        while len(files) > cls.MAX_BACKUPS:
            oldest = files.pop(0)
            os.remove(oldest)
            logger.info(f"🧹 Backup antiguo purgado: {oldest}")

if __name__ == "__main__":
    BackupManager.execute_backup()
