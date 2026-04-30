import logging
from flask import Flask, request, jsonify
import time

# 🌉 PUENTE FÍSICO (Hardware Bridge) - MOCK PROFESIONAL
# Carbones y Pollos TPV - Enterprise v2.6
# Este script emula la conexión con impresoras térmicas y cajones portamonedas.

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [HARDWARE] %(message)s"
)
logger = logging.getLogger("HardwareBridge")

@app.route('/webhook/imprimir', methods=['POST'])
def imprimir_ticket():
    data = request.json
    tipo = data.get("tipo", "GENERAL")
    ticket = data.get("numero_ticket", "S/N")
    origen = data.get("origen", "LOCAL")
    
    logger.info("="*40)
    logger.info(f"🖨️  IMPRIMIENDO TICKET: {ticket}")
    logger.info(f"📍 ORIGEN: {origen} | TIPO: {tipo}")
    logger.info("-" * 40)
    
    for item in data.get("items", []):
        logger.info(f"   {item.get('cantidad', 1)}x {item.get('producto_nombre', 'Producto')} ... {item.get('precio_unitario', 0):.2f}€")
    
    logger.info("-" * 40)
    logger.info(f"💰 TOTAL: {data.get('total', 0):.2f}€")
    logger.info("="*40)
    
    return jsonify({"status": "printed", "job_id": "job_12345"})

@app.route('/webhook/abrir_caja', methods=['POST'])
def abrir_caja():
    logger.warning("💸 [ALERTA] COMANDO DE APERTURA DE CAJÓN RECIBIDO")
    time.sleep(0.5)
    logger.info("✅ CAJÓN ABIERTO FÍSICAMENTE")
    return jsonify({"status": "opened"})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "online", "hardware": "connected"})

if __name__ == '__main__':
    print("="*50)
    print("🚀 HARDWARE BRIDGE MOCK INICIADO EN EL PUERTO 8080")
    print("Simulando conexión con Impresora Térmica y Cajón de Monedas.")
    print("="*50)
    app.run(port=8080)
