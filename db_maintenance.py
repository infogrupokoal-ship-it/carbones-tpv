import sqlite3
import os
import shutil
import datetime

DB_PATH = "tpv_data.sqlite"
BACKUP_DIR = "backups"

def run_maintenance():
    print("Iniciando Mantenimiento de Base de Datos...")
    
    # 1. Vacuum
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("VACUUM")
        conn.commit()
        conn.close()
        print("VACUUM completado con éxito. Espacio optimizado.")
    except Exception as e:
        print(f"Error durante VACUUM: {e}")
        
    # 2. Backup Local
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
        
    hoy_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"tpv_data_{hoy_str}.sqlite")
    
    try:
        shutil.copy2(DB_PATH, backup_file)
        print(f"Copia de seguridad guardada en: {backup_file}")
    except Exception as e:
        print(f"Error realizando la copia de seguridad: {e}")
        
    # 3. Limpieza de backups antiguos (mantener últimos 7)
    try:
        backups = sorted([f for f in os.listdir(BACKUP_DIR) if f.endswith(".sqlite")])
        if len(backups) > 7:
            for b_old in backups[:-7]:
                path_old = os.path.join(BACKUP_DIR, b_old)
                os.remove(path_old)
                print(f"Backup antiguo eliminado: {b_old}")
    except Exception as e:
        print(f"Error limpiando backups antiguos: {e}")
        
    print("Mantenimiento finalizado correctamente.")

if __name__ == "__main__":
    run_maintenance()
