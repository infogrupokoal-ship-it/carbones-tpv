import subprocess
import time
import sys
import os
import logging

# ConfiguraciÃ³n Profesional de Rutas
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
    filename=LOG_FILE,
    encoding="utf-8"
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)

def start_process(name, path):
    logging.info(f"[BOOT] Iniciando componente: {name} ({os.path.basename(path)})...")
    try:
        # Usamos creationflags para que no abran ventanas extra si se ejecuta desde VBS
        return subprocess.Popen([PYTHON_EXE, path], cwd=os.path.dirname(path))
    except Exception as e:
        logging.error(f"[ERROR] Error al iniciar {name}: {e}")
        return None

def monitor():
    logging.info("[INFO] Master Watchdog Industrializado activo.")
    processes = {name: None for name in SCRIPTS}
    
    while True:
        for name, path in SCRIPTS.items():
            proc = processes[name]
            if proc is None or proc.poll() is not None:
                if proc is not None:
                    logging.warning(f"[WARN] Componente {name} detenido (Exit Code: {proc.returncode}).")
                    time.sleep(2) # Pequeño delay para no saturar si hay fallo continuo
                processes[name] = start_process(name, path)
        
        time.sleep(10) # AuditorÃ­a cada 10 segundos

if __name__ == "__main__":
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    try:
        monitor()
    except KeyboardInterrupt:
        logging.info("[STOP] Master Watchdog detenido manualmente.")
        sys.exit(0)
