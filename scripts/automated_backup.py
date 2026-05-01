import os
import shutil
import datetime
import logging

# Configuración
SOURCE_DB = r"d:\proyecto\carbones_y_pollos_tpv\instance\tpv_data.sqlite"
SOURCE_LOGS = r"d:\proyecto\carbones_y_pollos_tpv\logs"
BACKUP_DIR = r"d:\proyecto\carbones_y_pollos_tpv_usb_backup"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=os.path.join(r"d:\proyecto\carbones_y_pollos_tpv\logs", "backup_service.log")
)

def perform_backup():
    try:
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_subdir = os.path.join(BACKUP_DIR, f"backup_{timestamp}")
        os.makedirs(backup_subdir)
        
        # Copiar DB
        if os.path.exists(SOURCE_DB):
            shutil.copy2(SOURCE_DB, os.path.join(backup_subdir, "tpv_data.sqlite"))
            logging.info(f"Base de datos respaldada en {backup_subdir}")
        else:
            logging.warning("No se encontró la base de datos para respaldar.")
            
        # Copiar Logs
        if os.path.exists(SOURCE_LOGS):
            shutil.copytree(SOURCE_LOGS, os.path.join(backup_subdir, "logs"), dirs_exist_ok=True)
            logging.info("Logs respaldados.")
            
        # Limpieza de backups antiguos (mantener los últimos 10)
        backups = sorted([d for d in os.listdir(BACKUP_DIR) if d.startswith("backup_")])
        if len(backups) > 10:
            for old_backup in backups[:-10]:
                shutil.rmtree(os.path.join(BACKUP_DIR, old_backup))
                logging.info(f"Backup antiguo eliminado: {old_backup}")
                
    except Exception as e:
        logging.error(f"Error crítico en el servicio de backup: {e}")

if __name__ == "__main__":
    perform_backup()
