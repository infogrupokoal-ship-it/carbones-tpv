# local_print_bridge.py
# Bridge local Windows V2: Cola de impresión, reintentos, logs rotativos y estado.
import os
import time
import tempfile
import subprocess
import threading
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, request, jsonify

# --- CONFIGURACIÓN Y LOGS ---
os.makedirs("logs", exist_ok=True)
logger = logging.getLogger("PrintBridge")
logger.setLevel(logging.INFO)
handler = RotatingFileHandler("logs/print-bridge.log", maxBytes=1024*1024*5, backupCount=3, encoding="utf-8")
formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
# También a consola
console = logging.StreamHandler()
console.setFormatter(formatter)
logger.addHandler(console)

app = Flask(__name__)

PRINTER_NAME = os.getenv("PRINTER_NAME", "").strip()
PORT = int(os.getenv("BRIDGE_PORT", "8181"))

# --- COLA DE IMPRESIÓN Y ESTADO ---
print_queue = []
job_history = []
queue_lock = threading.Lock()

def print_text_windows(text: str, printer_name: str = ""):
    """Envía texto a la impresora en Windows usando PowerShell y Notepad."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8") as f:
        f.write(text)
        path = f.name

    try:
        if printer_name:
            ps = (
                f'$p="{path}"; '
                f'$printer="{printer_name}"; '
                f'Start-Process -FilePath notepad.exe -ArgumentList "/p `"$p`"" -WindowStyle Hidden; '
                f'Start-Sleep -Milliseconds 800; '
                f'"OK"'
            )
        else:
            ps = (
                f'$p="{path}"; '
                f'Start-Process -FilePath notepad.exe -ArgumentList "/p `"$p`"" -WindowStyle Hidden; '
                f'Start-Sleep -Milliseconds 800; '
                f'"OK"'
            )

        completed = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps],
            capture_output=True, text=True, timeout=15
        )

        if completed.returncode != 0:
            return False, f"PowerShell error: {completed.stderr.strip()}"

        return True, "Printed successfully"
    except Exception as e:
        return False, f"Exception: {str(e)}"
    finally:
        try:
            os.remove(path)
        except Exception:
            pass

# --- HILO DE PROCESAMIENTO (WORKER) ---
def queue_worker():
    """Procesa la cola de impresión en segundo plano."""
    logger.info("Print Queue Worker iniciado.")
    while True:
        job_to_process = None
        with queue_lock:
            if print_queue:
                job_to_process = print_queue.pop(0)

        if job_to_process:
            job_id = job_to_process['id']
            text = job_to_process['ticket']
            retries = job_to_process['retries']
            
            logger.info(f"Procesando Job {job_id} (Intento {4 - retries})")
            ok, detail = print_text_windows(text, PRINTER_NAME)
            
            if ok:
                logger.info(f"Job {job_id} completado con éxito.")
                job_to_process['status'] = 'completed'
                job_to_process['detail'] = detail
            else:
                logger.error(f"Job {job_id} falló: {detail}")
                if retries > 0:
                    job_to_process['retries'] -= 1
                    job_to_process['status'] = 'pending_retry'
                    logger.info(f"Re-encolando Job {job_id}. Reintentos restantes: {job_to_process['retries']}")
                    time.sleep(2)  # Pausa antes del reintento
                    with queue_lock:
                        print_queue.insert(0, job_to_process) # Poner al principio
                else:
                    job_to_process['status'] = 'failed'
                    job_to_process['detail'] = f"Agotados reintentos. Último error: {detail}"
                    logger.error(f"Job {job_id} abandonado. Agotados reintentos.")
        else:
            time.sleep(1) # Esperar si la cola está vacía

# Iniciar hilo de procesamiento
worker_thread = threading.Thread(target=queue_worker, daemon=True)
worker_thread.start()


# --- RUTAS DE LA API ---
@app.get("/health")
def health():
    return jsonify({
        "ok": True,
        "service": "local-print-bridge-v2",
        "printer": PRINTER_NAME or "(default)",
        "port": PORT,
        "queue_size": len(print_queue)
    })

@app.get("/last-jobs")
def get_last_jobs():
    """Retorna los últimos 20 trabajos de impresión para trazabilidad."""
    # Retornar del más reciente al más antiguo
    return jsonify(list(reversed(job_history[-20:])))

@app.post("/print")
def print_endpoint():
    data = request.get_json(silent=True) or {}
    ticket = data.get("ticket", "")
    
    if not ticket:
        logger.warning("Intento de impresión sin texto de ticket.")
        return jsonify({"ok": False, "message": "Missing 'ticket' text"}), 400

    job_id = f"job_{int(time.time()*1000)}"
    
    job = {
        "id": job_id,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "ticket": ticket,
        "retries": 3, # Hasta 3 reintentos automáticos
        "status": "queued",
        "detail": ""
    }

    with queue_lock:
        print_queue.append(job)
        job_history.append(job)
        # Limitar historial a 100 elementos
        if len(job_history) > 100:
            job_history.pop(0)

    logger.info(f"Job {job_id} añadido a la cola de impresión.")
    return jsonify({"ok": True, "message": "Encolado", "job_id": job_id}), 202

if __name__ == "__main__":
    logger.info(f"Iniciando Local Print Bridge V2 en puerto {PORT}")
    app.run(host="127.0.0.1", port=PORT, debug=False, use_reloader=False)
