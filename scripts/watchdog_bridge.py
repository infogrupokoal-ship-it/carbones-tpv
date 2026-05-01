import subprocess
import time
import sys
import os
import logging

# Configuración
BRIDGE_SCRIPT = r"d:\proyecto\carbones_y_pollos_tpv\local_printer_bridge.py"
PYTHON_EXE = sys.executable
LOG_FILE = r"d:\proyecto\carbones_y_pollos_tpv\logs\watchdog.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=LOG_FILE
)

def start_bridge():
    logging.info("🚀 Iniciando el puente de hardware (local_printer_bridge)...")
    try:
        # Iniciamos el proceso y esperamos
        process = subprocess.Popen([PYTHON_EXE, BRIDGE_SCRIPT])
        return process
    except Exception as e:
        logging.error(f"Error al iniciar el puente: {e}")
        return None

def monitor():
    logging.info("🐕 Perro Guardián (Watchdog) activo.")
    process = start_bridge()
    
    while True:
        if process is None or process.poll() is not None:
            logging.warning("⚠️ El puente se ha detenido o no pudo iniciar. Reiniciando en 5 segundos...")
            time.sleep(5)
            process = start_bridge()
        
        time.sleep(10) # Verificar cada 10 segundos

if __name__ == "__main__":
    # Asegurar que el directorio de logs existe
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    monitor()
