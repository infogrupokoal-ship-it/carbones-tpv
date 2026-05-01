import subprocess
import time
import sys
import os
import logging

# Configuración Profesional de Rutas
BASE_DIR = r"d:\proyecto\carbones_y_pollos_tpv"
SCRIPTS = {
    "BRIDGE": os.path.join(BASE_DIR, "local_printer_bridge.py"),
    "SYNC": os.path.join(BASE_DIR, "sync_daemon.py")
}
PYTHON_EXE = sys.executable
LOG_FILE = os.path.join(BASE_DIR, "logs", "master_watchdog.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - [MASTER_WATCHDOG] - %(message)s',
    filename=LOG_FILE
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)

def start_process(name, path):
    logging.info(f"🚀 Iniciando componente: {name} ({os.path.basename(path)})...")
    try:
        # Usamos creationflags para que no abran ventanas extra si se ejecuta desde VBS
        return subprocess.Popen([PYTHON_EXE, path])
    except Exception as e:
        logging.error(f"❌ Error al iniciar {name}: {e}")
        return None

def monitor():
    logging.info("🐕 Master Watchdog Industrializado activo.")
    processes = {name: None for name in SCRIPTS}
    
    while True:
        for name, path in SCRIPTS.items():
            proc = processes[name]
            if proc is None or proc.poll() is not None:
                if proc is not None:
                    logging.warning(f"⚠️ Componente {name} se detuvo inesperadamente (Exit Code: {proc.returncode}).")
                processes[name] = start_process(name, path)
        
        time.sleep(10) # Auditoría cada 10 segundos

if __name__ == "__main__":
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    try:
        monitor()
    except KeyboardInterrupt:
        logging.info("🛑 Master Watchdog detenido manualmente.")
        sys.exit(0)
