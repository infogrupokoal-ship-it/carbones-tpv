import sqlite3
import os
import shutil
import datetime
import requests
import base64

DB_PATH = "tpv_data.sqlite"
BACKUP_DIR = "backups"

WAHA_URL = os.environ.get("WAHA_URL", "http://113.30.148.104:3000")
WAHA_SESSION = os.environ.get("WAHA_SESSION", "carbones")
WAHA_API_KEY = os.environ.get("WAHA_HTTP_API_KEY", "1060705b0a574d1fbc92fa10a2b5aca7")
TELEFONO_ADMIN = os.environ.get("TELEFONO_ADMIN", "34604864187")

def enviar_backup_whatsapp(filepath):
    print(f"Preparando envío de {filepath} por WAHA...")
    try:
        with open(filepath, "rb") as f:
            b64_data = base64.b64encode(f.read()).decode("utf-8")
        
        filename = os.path.basename(filepath)
        data_uri = f"data:application/x-sqlite3;base64,{b64_data}"
        
        payload = {
            "chatId": f"{TELEFONO_ADMIN}@c.us",
            "file": {
                "mimetype": "application/x-sqlite3",
                "filename": filename,
                "url": data_uri
            },
            "caption": f"💾 Backup Semanal de Base de Datos ({filename})",
            "session": WAHA_SESSION
        }
        
        headers = {"Content-Type": "application/json"}
        if WAHA_API_KEY:
            headers["X-Api-Key"] = WAHA_API_KEY
            
        res = requests.post(f"{WAHA_URL}/api/sendFile", json=payload, headers=headers, timeout=30)
        if res.status_code in [200, 201]:
            print("Backup enviado por WhatsApp correctamente.")
        else:
            print(f"Error WAHA: {res.text}")
    except Exception as e:
        print(f"Excepción enviando backup: {e}")

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
        
        # Enviar vía WhatsApp
        enviar_backup_whatsapp(backup_file)
        
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
