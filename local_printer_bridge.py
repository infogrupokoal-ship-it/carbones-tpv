import logging
import threading
import time
import os
import json
import sys
from datetime import datetime

import requests
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

# Intentar importar win32print para soporte de Windows
try:
    import win32print
    PRINT_ENABLED = True
except ImportError:
    PRINT_ENABLED = False

# Intentar importar el formateador de la lÃ³gica del proyecto
try:
    from backend.utils.printer import TicketFormatter
except ImportError:
    # Fallback si se ejecuta fuera del entorno del proyecto
    class TicketFormatter:
        @staticmethod
        def format_client_ticket(d): 
            return f"TICKET CLIENTE {d.get('numero_ticket')}\nTOTAL: {d.get('total')}â‚¬"
        @staticmethod
        def format_kitchen_ticket(d): 
            return f"COMANDA COCINA {d.get('numero_ticket')}"

app = FastAPI(title="Carbones y Pollos - Puente Industrial v4.5")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ConfiguraciÃ³n
CONFIG_FILE = "instance/printer_config.json"
if not os.path.exists("instance"):
    os.makedirs("instance")

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {"impresora_ticket": "POS-80", "impresora_cocina": "POS-80", "cloud_url": "https://carbones-tpv.onrender.com"}

config = load_config()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [PRINTER_BRIDGE] %(message)s",
    handlers=[
        logging.FileHandler("instance/bridge.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("PrinterBridge")

# --- PID LOCK ---
PID_FILE = "instance/bridge.pid"

def acquire_lock():
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE, 'r') as f:
                old_pid = int(f.read().strip())
            if os.name == 'posix':
                import os as os_native
                os_native.kill(old_pid, 0)
            else:
                import ctypes
                PROCESS_QUERY_INFORMATION = 0x0400
                handle = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_INFORMATION, False, old_pid)
                if handle != 0:
                    ctypes.windll.kernel32.CloseHandle(handle)
                else:
                    raise OSError
            logger.error(f"[LOCK] Bridge ya activo (PID: {old_pid}).")
            sys.exit(0)
        except (OSError, ValueError):
            os.remove(PID_FILE)
    with open(PID_FILE, 'w') as f:
        f.write(str(os.getpid()))

def release_lock():
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)

# --- ESTADO DE HARDWARE ---
hardware_status = {
    "printer_connected": False,
    "last_print_time": None,
    "last_error": None,
    "cloud_connection": False
}

def check_hardware():
    global hardware_status
    if PRINT_ENABLED:
        try:
            printers = [p[2] for p in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL)]
            hardware_status["printer_connected"] = config["impresora_ticket"] in printers
        except Exception as e:
            logger.error(f"Error detectando impresoras: {e}")
            hardware_status["printer_connected"] = False
    else:
        # En Android asumimos que RawBT estÃ¡ ahÃ­ o simplemente reportamos modo Termux
        hardware_status["printer_connected"] = True 

@app.get("/api/status")
async def get_status():
    check_hardware()
    return hardware_status

@app.get("/", response_class=HTMLResponse)
async def pagina_instalacion():
    html = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>TPV Bridge Control Center</title>
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap" rel="stylesheet">
        <style>
            :root { --primary: #ef4444; --bg: #0f172a; --card: #1e293b; }
            body { font-family: 'Outfit', sans-serif; background: var(--bg); color: white; padding: 40px; max-width: 800px; margin: auto; }
            .status-bar { background: var(--card); padding: 20px; border-radius: 12px; display: flex; gap: 20px; margin-bottom: 30px; border-left: 5px solid var(--primary); }
            .indicator { display: flex; align-items: center; gap: 8px; font-size: 14px; }
            .dot { width: 12px; height: 12px; border-radius: 50%; background: #4ade80; }
            .dot.off { background: #f87171; }
            .card { background: var(--card); padding: 30px; border-radius: 16px; margin-bottom: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.3); }
            h1 { color: var(--primary); margin-top: 0; font-weight: 600; }
            .code-box { background: #000; color: #10b981; padding: 20px; border-radius: 8px; font-family: 'Courier New', monospace; font-size: 13px; overflow-x: auto; margin: 15px 0; border: 1px solid #334155; }
            button { background: var(--primary); color: white; border: none; padding: 12px 24px; border-radius: 8px; cursor: pointer; font-weight: 600; transition: 0.3s; width: 100%; }
            button:hover { opacity: 0.9; transform: translateY(-2px); }
            .secondary { background: #3b82f6; margin-top: 10px; }
        </style>
    </head>
    <body>
        <h1>[BOOT] TPV Bridge Control Center</h1>
        <div class="status-bar">
            <div class="indicator"><div class="dot" id="dot-print"></div> Impresora: <span id="txt-print">Detectando...</span></div>
            <div class="indicator"><div class="dot" id="dot-cloud"></div> Cloud: <span id="txt-cloud">Conectando...</span></div>
        </div>

        <div class="card">
            <h2>[SETUP] Instalación en un Toque</h2>
            <p>Ejecuta este comando en tu terminal local para sincronizar con la nube:</p>
            <div class="code-box">curl -sSL https://carbones-tpv.onrender.com/static/setup.sh | bash</div>
            <button onclick="navigator.clipboard.writeText('curl -sSL https://carbones-tpv.onrender.com/static/setup.sh | bash')">COPIAR COMANDO MAESTRO</button>
        </div>

        <script>
            async function updateStatus() {
                try {
                    const res = await fetch('/api/status');
                    const data = await res.json();
                    document.getElementById('dot-print').className = data.printer_connected ? 'dot' : 'dot off';
                    document.getElementById('txt-print').innerText = data.printer_connected ? 'CONECTADA' : 'NO DETECTADA';
                    document.getElementById('dot-cloud').className = data.cloud_connection ? 'dot' : 'dot off';
                    document.getElementById('txt-cloud').innerText = data.cloud_connection ? 'ONLINE' : 'OFFLINE';
                } catch(e) {}
            }
            setInterval(updateStatus, 3000);
            updateStatus();
        </script>
    </body>
    </html>
    """
    return html

def print_raw(printer_name, content):
    global hardware_status
    if PRINT_ENABLED:
        try:
            h = win32print.OpenPrinter(printer_name)
            try:
                win32print.StartDocPrinter(h, 1, ("TPV Ticket", None, "RAW"))
                win32print.StartPagePrinter(h)
                win32print.WritePrinter(h, content.encode("cp850") if isinstance(content, str) else content)
                win32print.EndPagePrinter(h)
                win32print.EndDocPrinter(h)
                hardware_status["last_print_time"] = datetime.now().isoformat()
                return True
            finally:
                win32print.ClosePrinter(h)
        except Exception as e:
            hardware_status["last_error"] = str(e)
            logger.error(f"Fallo impresiÃ³n Windows: {e}")
            return False
    else:
        # Modo Android / RawBT
        try:
            res = requests.post("http://127.0.0.1:40213/", data=content.encode("utf-8") if isinstance(content, str) else content, timeout=3)
            return res.status_code == 200
        except Exception as e:
            logger.error(f"Fallo conexiÃ³n RawBT: {e}")
            return False

@app.post("/webhook/imprimir")
async def webhook_print(request: Request):
    data = await request.json()
    tipo = data.get("tipo", "cliente")
    ticket = TicketFormatter.format_client_ticket(data) if tipo == "cliente" else TicketFormatter.format_kitchen_ticket(data)
    dest = config["impresora_ticket"] if tipo == "cliente" else config["impresora_cocina"]
    if print_raw(dest, ticket):
        return {"status": "ok"}
    return {"status": "error", "detail": hardware_status["last_error"]}

def hardware_loop():
    global hardware_status
    while True:
        try:
            res = requests.get(f"{config['cloud_url']}/api/hardware/poll", timeout=5)
            hardware_status["cloud_connection"] = True
            if res.status_code == 200:
                for cmd in res.json().get("comandos", []):
                    action = cmd['accion']
                    logger.info(f"Comando Nube: {action}")
                    
                    if action == "abrir_caja":
                        print_raw(config["impresora_ticket"], "\x1b\x70\x00\x19\xfa")
                    elif action == "imprimir":
                        ticket = TicketFormatter.format_client_ticket(cmd['payload'])
                        print_raw(config["impresora_ticket"], ticket)
                    
                    requests.post(f"{config['cloud_url']}/api/hardware/ack/{cmd['id']}")
        except Exception as e:
            logger.error(f"Error en loop de hardware: {e}")
            hardware_status["cloud_connection"] = False
        time.sleep(10)

if __name__ == "__main__":
    acquire_lock()
    try:
        threading.Thread(target=hardware_loop, daemon=True).start()
        uvicorn.run(app, host="0.0.0.0", port=8001)
    finally:
        release_lock()
