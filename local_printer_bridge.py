import logging
import threading
import time
import json
import os
from datetime import datetime

import requests
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from backend.utils.printer import TicketFormatter

# Dependencias para imprimir en Windows (Asegúrate de instalarlas: pip install pypiwin32)
try:
    import win32print

    PRINT_ENABLED = True
except ImportError:
    PRINT_ENABLED = False
    print(
        "Advertencia: No se encontraron librerías de impresión de Windows. Usa 'pip install pypiwin32'"
    )

app = FastAPI(title="Carbones y Pollos - Puente de Impresión Local")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- INSTALADOR WEB DE AUTO-ARRANQUE ---
@app.get("/", response_class=HTMLResponse)
async def pagina_instalacion():
    html = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Instalación TPV y Puertas</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f3f4f6; color: #111827; padding: 20px; display: flex; flex-direction: column; align-items: center; }
            .card { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); max-width: 600px; width: 100%; text-align: center; margin-bottom: 20px; }
            h1 { color: #ef4444; }
            h2 { color: #8b5cf6; margin-top: 0; }
            p { font-size: 16px; line-height: 1.5; color: #4b5563; }
            .code-box { background: #1f2937; color: #10b981; padding: 20px; border-radius: 8px; font-family: monospace; font-size: 14px; margin: 20px 0; word-break: break-all; user-select: all; cursor: pointer; position: relative; text-align: left;}
            .copy-btn { background: #3b82f6; color: white; border: none; padding: 15px; font-size: 16px; font-weight: bold; border-radius: 8px; cursor: pointer; width: 100%; margin-top: 10px; }
            .copy-btn:hover { background: #2563eb; }
            .copy-btn.purple { background: #8b5cf6; }
            .copy-btn.purple:hover { background: #7c3aed; }
            .success { color: #16a34a; font-weight: bold; margin-top: 15px; display: none; }
            .step { background: #e0e7ff; color: #3730a3; padding: 15px; border-radius: 8px; margin-top: 20px; text-align: left; font-size: 15px;}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>⚙️ 1. Instalador TPV (Principal)</h1>
            <p>Pulsa el botón azul para copiar el comando, pégalo en Termux y dale a Enter para instalar el puente del TPV.</p>
            <div class="code-box" id="codigoInstalador">pkg update -y; pkg install -y git python; rm -rf ~/carbones-tpv; git clone https://github.com/infogrupokoal-ship-it/carbones-tpv.git ~/carbones-tpv; cd ~/carbones-tpv && pip install fastapi uvicorn requests pydantic && python local_printer_bridge.py</div>
            <button class="copy-btn" onclick="copiarCodigo('codigoInstalador', 'msgInstalador')">📥 COPIAR COMANDO DE INSTALACIÓN</button>
            <div id="msgInstalador" class="success">✅ ¡Copiado! Ahora pégalo en Termux.</div>
        </div>

        <div class="card">
            <h2>🚪 2. Puertas de Control Remoto (Antigravity)</h2>
            <p>Ejecuta estos comandos en Termux uno a uno para habilitar el control remoto.</p>
            
            <div class="step"><strong>Paso A:</strong> Instalar Servidor SSH y configurar Contraseña</div>
            <div class="code-box" id="codigoSSH">pkg install -y openssh && sshd && passwd</div>
            <button class="copy-btn purple" onclick="copiarCodigo('codigoSSH', 'msgSSH')">🔑 COPIAR COMANDO SSH</button>
            <div id="msgSSH" class="success">✅ ¡Copiado! Pégalo en Termux. (Te pedirá que escribas una contraseña dos veces).</div>

            <div class="step"><strong>Paso B:</strong> Crear el Túnel Global (Pinggy)</div>
            <div class="code-box" id="codigoNgrok">ssh -o StrictHostKeyChecking=no -p 443 -R0:localhost:8022 a.pinggy.io</div>
            <button class="copy-btn purple" onclick="copiarCodigo('codigoNgrok', 'msgNgrok')">🌐 COPIAR COMANDO TÚNEL</button>
            <div id="msgNgrok" class="success">✅ ¡Copiado! Pégalo en Termux.</div>
        </div>

        <div class="card">
            <h2>🚀 3. Auto-Arranque (Inmortal)</h2>
            <p>Pega este comando para que el puente arranque solo siempre que enciendas la tablet.</p>
            <div class="code-box" id="codigoArranque">mkdir -p ~/.termux/boot && echo "termux-wake-lock; cd ~/carbones-tpv; git pull origin master; nohup python local_printer_bridge.py > bridge.log 2>&1 &" > ~/.termux/boot/start.sh && chmod +x ~/.termux/boot/start.sh</div>
            <button class="copy-btn" style="background:#059669;" onclick="copiarCodigo('codigoArranque', 'msgArranque')">⚡ COPIAR COMANDO ARRANQUE</button>
            <div id="msgArranque" class="success">✅ ¡Copiado! Pégalo en Termux.</div>
        </div>

        <script>
            function copiarCodigo(idElemento, idMensaje) {
                const texto = document.getElementById(idElemento).innerText;
                navigator.clipboard.writeText(texto).then(() => {
                    document.getElementById(idMensaje).style.display = 'block';
                    setTimeout(() => document.getElementById(idMensaje).style.display = 'none', 3000);
                }).catch(err => {
                    alert('No se pudo copiar automáticamente.');
                });
            }
        </script>
    </body>
    </html>
    """
    return html


# ------------------------------------------------------------
# CONFIGURACIÓN: Nombra tu impresora térmica exactamente
# como aparece en "Dispositivos e impresoras" de Windows.
# ------------------------------------------------------------
NOMBRE_IMPRESORA_TICKET = "POS-80"
NOMBRE_IMPRESORA_COCINA = "POS-80"  # Puede ser otra diferente si tienes 2

CLOUD_URL = os.environ.get("CLOUD_URL", "https://carbones-tpv.onrender.com")
DEVICE_ID = os.environ.get("DEVICE_ID", "CAJA-PRINCIPAL-01")

# Configuración de Logging Profesional con rotación
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("bridge_errors.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("PrinterBridge")


def imprimir_texto_crudo(nombre_impresora, texto_ticket):
    """Envía texto crudo (ESC/POS) o texto normal a la impresora térmica"""
    # Mandar a la impresora fìsica o App Android
    if PRINT_ENABLED:
        try:
            hprinter = win32print.OpenPrinter(nombre_impresora)
            try:
                win32print.StartDocPrinter(
                    hprinter, 1, ("Ticket Restaurante", None, "RAW")
                )
                win32print.StartPagePrinter(hprinter)
                win32print.WritePrinter(
                    hprinter, texto_ticket.encode("cp850")
                )  # O "utf-8" dependiendo del firmware de la térmica
                win32print.EndPagePrinter(hprinter)
                win32print.EndDocPrinter(hprinter)
                print(
                    f"[{datetime.now()}] TICKET ENVIADO A LA COLA DE {nombre_impresora}"
                )
            finally:
                win32print.ClosePrinter(hprinter)
        except Exception as e:
            print(f"Error al imprimir en Windows: {e}")
            return False
    else:
        # SISTEMA ANDROID (Termux)
        # Nos comunicamos con RawBT a través de su servidor WebSocket/HTTP interno (Puerto 40213)
        # Esto permite enviar binarios (como la apertura de caja) sin corromperse por Intents de texto.
        print(
            f"[{datetime.now()}] ENVIANDO TICKET A RAWBT (ANDROID) para {nombre_impresora}"
        )
        try:
            import urllib.request

            # Enviar el texto (o secuencia ESC/POS binaria) a la API local de RawBT
            url = "http://127.0.0.1:40213/"
            data = (
                texto_ticket.encode("utf-8")
                if isinstance(texto_ticket, str)
                else texto_ticket
            )
            req = urllib.request.Request(url, data=data, method="POST")
            req.add_header("Content-Type", "text/plain")

            with urllib.request.urlopen(req, timeout=3) as response:
                if response.status == 200:
                    print("=> Enviado a RawBT con éxito.")
                else:
                    print(f"=> RawBT respondió con código {response.status}.")
        except Exception as ex:
            print(
                f"=> Error conectando con RawBT: {ex}. ¿Está la app RawBT instalada y con el servidor activado?"
            )

    return True


@app.post("/webhook/imprimir")
async def recibir_ticket(request: Request):
    """
    Este es el endpoint seguro que Ngrok expondrá.
    El VPS de la IA mandará un POST aquí con los datos del pedido.
    """
    payload = await request.json()

    tipo_ticket = payload.get("tipo", "cliente")  # "cliente" o "cocina"
    payload.get("numero_ticket", "T-00")
    payload.get("origen", "MOSTRADOR")
    payload.get("items", [])
    payload.get("total", 0.0)

    # Fiscalidad
    payload.get("cuota_iva_10", 0.0)
    payload.get("base_imponible_10", 0.0)
    payload.get("cuota_iva_21", 0.0)
    payload.get("base_imponible_21", 0.0)

    payload.get("notas_cliente", "")

    datetime.now().strftime("%d/%m/%Y %H:%M")

    ticket = ""

    if tipo_ticket == "cliente":
        ticket = TicketFormatter.format_client_ticket(payload)
        impresora_destino = NOMBRE_IMPRESORA_TICKET
    else:
        ticket = TicketFormatter.format_kitchen_ticket(payload)
        impresora_destino = NOMBRE_IMPRESORA_COCINA

    # Mandar a la impresora fìsica
    exito = imprimir_texto_crudo(impresora_destino, ticket)

    if exito:
        return {"status": "ok", "msj": f"Impreso en {impresora_destino}"}
    else:
        return {"status": "error", "msj": "Fallo en la impresora local"}


@app.post("/webhook/abrir_caja")
async def abrir_caja():
    """
    Envía la secuencia binaria estándar ESC/POS para abrir el cajón
    portamonedas a través del puerto de la impresora.
    """
    # Secuencia para puerto 1, pulso de 25ms x 2 (aprox) -> ESC p 0 25 250
    secuencia_apertura = "\x1b\x70\x00\x19\xfa"
    exito = imprimir_texto_crudo(NOMBRE_IMPRESORA_TICKET, secuencia_apertura)

    if exito:
        return {"status": "ok", "msj": "Cajón abierto"}
    else:
        return {"status": "error", "msj": "Error abriendo cajón"}


def hardware_polling_loop():
    while True:
        try:
            res = requests.get(f"{CLOUD_URL}/api/hardware/poll", timeout=5)
            if res.status_code == 200:
                data = res.json()
                for cmd in data.get("comandos", []):
                    accion = cmd.get("accion")
                    payload = cmd.get("payload")

                    if accion == "abrir_caja":
                        logger.info(f"Comando ejecutado: ABRIR CAJA (ID: {cmd['id']})")
                        secuencia_apertura = "\x1b\x70\x00\x19\xfa"
                        imprimir_texto_crudo(NOMBRE_IMPRESORA_TICKET, secuencia_apertura)
                        requests.post(f"{CLOUD_URL}/api/hardware/ack/{cmd['id']}")

                    elif accion == "imprimir" and payload:
                        print(
                            f"[{datetime.now()}] Ejecutando comando nube: IMPRIMIR (ID: {cmd['id']})"
                        )

                        # Reutilizamos la lógica que ya teníamos en el webhook local
                        tipo_ticket = payload.get("tipo", "cliente")
                        payload.get("numero_ticket", "T-00")
                        payload.get("origen", "MOSTRADOR")
                        payload.get("items", [])
                        payload.get("total", 0.0)

                        payload.get("cuota_iva_10", 0.0)
                        payload.get("base_imponible_10", 0.0)
                        payload.get("cuota_iva_21", 0.0)
                        payload.get("base_imponible_21", 0.0)

                        payload.get("notas_cliente", "")

                        datetime.now().strftime("%d/%m/%Y %H:%M")
                        ticket = ""

                        if tipo_ticket == "cliente":
                            ticket = TicketFormatter.format_client_ticket(payload)
                            impresora_destino = NOMBRE_IMPRESORA_TICKET
                        else:
                            ticket = TicketFormatter.format_kitchen_ticket(payload)
                            impresora_destino = NOMBRE_IMPRESORA_COCINA

                        exito = imprimir_texto_crudo(impresora_destino, ticket)
                        if exito:
                            requests.post(f"{CLOUD_URL}/api/hardware/ack/{cmd['id']}")

        except Exception:
            # Silencioso para no ensuciar consola
            pass
        time.sleep(5)


if __name__ == "__main__":
    print("\n--- SERVIDOR DE IMPRESION LOCAL (PUENTE) INICIADO ---")
    print("El puente ahora escucha a la Nube mediante Polling.")
    print("------------------------------------------------------\n")

    # Iniciar polling thread para recibir comandos Cloud -> Edge
    t = threading.Thread(target=hardware_polling_loop, daemon=True)
    t.start()

    uvicorn.run(app, host="0.0.0.0", port=8000)
