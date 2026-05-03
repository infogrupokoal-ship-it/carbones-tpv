import os
import subprocess
import time
import sys

def cleanup():
    print("--- INICIANDO LIMPIEZA TOTAL ---")
    # Matar procesos por nombre de imagen
    subprocess.run(["taskkill", "/f", "/im", "python.exe"], capture_output=True)
    subprocess.run(["taskkill", "/f", "/im", "cmd.exe", "/fi", "WINDOWTITLE eq KOAL*"], capture_output=True)
    
    # Borrar archivos de bloqueo
    base_dir = r"D:\proyecto\carbones_y_pollos_tpv"
    instance_dir = os.path.join(base_dir, "instance")
    for f in ["bridge.pid", "sync_daemon.pid"]:
        path = os.path.join(instance_dir, f)
        if os.path.exists(path):
            try:
                os.remove(path)
                print(f"Eliminado: {f}")
            except:
                pass
    
    print("--- REINICIANDO SERVICIOS ---")
    # Iniciar Watchdog
    subprocess.Popen(["cmd", "/c", "watchdog_bridge.bat"], cwd=base_dir, creationflags=subprocess.CREATE_NEW_CONSOLE)
    
    # Iniciar Backend
    env = os.environ.copy()
    env["PYTHONPATH"] = "."
    subprocess.Popen([sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"], cwd=base_dir, env=env, creationflags=subprocess.CREATE_NEW_CONSOLE)
    
    print("--- SISTEMA REINICIADO ---")

if __name__ == "__main__":
    cleanup()
