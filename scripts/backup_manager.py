import os
import shutil
import datetime
import tarfile
import logging

# Gestor de Copias de Seguridad Enterprise
# Carbones y Pollos TPV

DB_PATH = "tpv_data.sqlite"
BACKUP_DIR = "backups"
LOG_DIR = "instance/logs"
MAX_BACKUPS = 7

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("BackupManager")

def create_backup():
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
        
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"tpv_enterprise_backup_{timestamp}.tar.gz")
    
    logger.info(f"Iniciando copia de seguridad: {backup_file}")
    
    try:
        with tarfile.open(backup_file, "w:gz") as tar:
            # Añadir Base de Datos
            if os.path.exists(DB_PATH):
                tar.add(DB_PATH, arcname="tpv_data.sqlite")
            
            # Añadir Logs Críticos
            if os.path.exists(LOG_DIR):
                tar.add(LOG_DIR, arcname="logs")
            
            # Añadir Configuración
            if os.path.exists(".env"):
                tar.add(".env", arcname="config.env")
                
        logger.info("Copia de seguridad completada con éxito.")
        rotate_backups()
    except Exception as e:
        logger.error(f"Fallo en la copia de seguridad: {e}")

def rotate_backups():
    """Mantiene solo los últimos N backups para optimizar espacio en disco."""
    backups = sorted(
        [os.path.join(BACKUP_DIR, f) for f in os.listdir(BACKUP_DIR) if f.endswith(".tar.gz")],
        key=os.path.getmtime
    )
    
    while len(backups) > MAX_BACKUPS:
        old_backup = backups.pop(0)
        os.remove(old_backup)
        logger.info(f"Backup antiguo eliminado: {old_backup}")

if __name__ == "__main__":
    create_backup()
