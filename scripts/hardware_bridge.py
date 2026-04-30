import time
import requests
import json
import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, request, jsonify
from flask_cors import CORS
import threading

# ==============================================================================
# 🌉 PUENTE FÍSICO (Hardware Bridge) - EDGE COMPUTING SERVICE
# Carbones y Pollos TPV - Enterprise v3.0
# ==============================================================================

app = Flask(__name__)
# Permitir llamadas CORS en caso de que el TPV web intente imprimir directamente vía red local
CORS(app)

# --- CONFIGURACIÓN DE LOGGING ROTATIVO ---
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'instance', 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
log_file = os.path.join(LOG_DIR, 'hardware_bridge.log')

formatter = logging.Formatter('%(asctime)s [%(levelname)s] [HARDWARE] %(message)s')
handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=3)
handler.setFormatter(formatter)

logger = logging.getLogger("HardwareBridge")
logger.setLevel(logging.INFO)
logger.addHandler(handler)
# También mostrar en consola
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# --- ENDPOINTS LOCALES PARA WEBHOOKS ---
@app.route('/webhook/imprimir', methods=['POST'])
def imprimir_ticket():
    try:
        data = request.json
        tipo = data.get("tipo", "GENERAL")
        ticket = data.get("numero_ticket", "S/N")
        origen = data.get("origen", "LOCAL")
        
        logger.info("="*40)
        logger.info(f"🖨️  IMPRIMIENDO TICKET: {ticket}")
        logger.info(f"📍 ORIGEN: {origen} | TIPO: {tipo}")
        logger.info("-" * 40)
        
        # Aquí se inyectaría la librería de la impresora real (ej. python-escpos)
        for item in data.get("items", []):
            logger.info(f"   {item.get('cantidad', 1)}x {item.get('producto_nombre', 'Producto')} ... {item.get('precio_unitario', 0):.2f}€")
        
        logger.info("-" * 40)
        logger.info(f"💰 TOTAL: {data.get('total', 0):.2f}€")
        logger.info("="*40)
        
        return jsonify({"status": "printed", "job_id": f"job_{int(time.time())}"}), 200
    except Exception as e:
        logger.error(f"Error al procesar impresión: {str(e)}")
        return jsonify({"status": "error", "message": "Fallo en impresora física"}), 500

@app.route('/webhook/abrir_caja', methods=['POST'])
def abrir_caja():
    try:
        logger.warning("💸 [ALERTA] COMANDO DE APERTURA DE CAJÓN RECIBIDO")
        # Aquí iría el código real (e.g. envio de hex a impresora: b'\x1B\x70\x00\x19\xFA')
        time.sleep(0.5)
        logger.info("✅ CAJÓN ABIERTO FÍSICAMENTE")
        return jsonify({"status": "opened"}), 200
    except Exception as e:
        logger.error(f"Error al abrir cajón: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "online", 
        "hardware": "simulated", 
        "version": "3.0"
    }), 200

# --- BACKGROUND POLLER (OPCIONAL) ---
# Este hilo puede preguntar activamente a tu VPS si hay órdenes pendientes
# en caso de que no haya IP pública local para webhooks directos.
def cloud_polling_worker():
    VPS_URL = os.getenv("VPS_URL", "http://113.30.148.104/api/hardware/pending")
    logger.info(f"Iniciando hilo de Polling a {VPS_URL} (Desactivado por defecto)")
    while True:
        try:
            # r = requests.get(VPS_URL, timeout=5)
            # if r.status_code == 200 and r.json().get('jobs'):
            #    for job in r.json().get('jobs'):
            #        # Procesar job...
            pass
        except Exception as e:
            pass
        time.sleep(10)

if __name__ == '__main__':
    print("="*60)
    print("🚀 HARDWARE BRIDGE (EDGE SERVICE) INICIADO")
    print(f"Log Output: {log_file}")
    print("Simulando conexión ESC/POS con Impresora y Cajón.")
    print("="*60)
    
    # Iniciar polling thread si es necesario
    # poller = threading.Thread(target=cloud_polling_worker, daemon=True)
    # poller.start()
    
    app.run(host="0.0.0.0", port=8080)
