import os
import time
import json
import logging
import requests
from dotenv import load_dotenv

# Configurar logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("printer_poller.log")
    ]
)
logger = logging.getLogger(__name__)

# Cargar variables de entorno locales
load_dotenv()

# Configuración
API_BASE_URL = os.getenv("RENDER_API_URL", "https://carbones-tpv.onrender.com/api")
POLL_INTERVAL = int(os.getenv("PRINTER_POLL_INTERVAL", 5))
PRINTER_HOST = os.getenv("LOCAL_PRINTER_HOST", "192.168.1.200")
PRINTER_PORT = int(os.getenv("LOCAL_PRINTER_PORT", 9100))

# Intentar importar la clase de impresión y formateo (si el script corre en el mismo repo)
try:
    from backend.utils.printer import EscPosPrinter, TicketFormatter
    PRINTER_AVAILABLE = True
except ImportError:
    logger.warning("No se pudo importar EscPosPrinter/TicketFormatter. Se imprimirán logs en consola como fallback.")
    PRINTER_AVAILABLE = False


def print_ticket_locally(payload: dict):
    """
    Formatea y envía a la impresora térmica local.
    """
    if not PRINTER_AVAILABLE:
        logger.info(f"🖨️ [DRY-RUN] Imprimiendo ticket {payload.get('numero_ticket')}")
        return True

    try:
        printer = EscPosPrinter(host=PRINTER_HOST, port=PRINTER_PORT)
        tipo = payload.get("tipo", "cliente")
        
        if tipo == "cocina":
            texto = TicketFormatter.format_kitchen_ticket(payload)
        else:
            texto = TicketFormatter.format_client_ticket(payload)
            
        success = printer.print_ticket(texto)
        if success:
            logger.info(f"✅ Ticket {payload.get('numero_ticket')} ({tipo}) impreso correctamente en {PRINTER_HOST}.")
        else:
            logger.error(f"❌ Fallo al imprimir el ticket {payload.get('numero_ticket')} en {PRINTER_HOST}.")
        return success
    except Exception as e:
        logger.error(f"❌ Error crítico de impresión: {e}")
        return False


def poll_and_print():
    """
    Consulta trabajos pendientes y los imprime.
    """
    logger.info(f"Iniciando Local Printer Poller -> URL: {API_BASE_URL} | Intervalo: {POLL_INTERVAL}s")
    
    while True:
        try:
            # 1. Consultar comandos pendientes
            response = requests.get(f"{API_BASE_URL}/hardware/poll", timeout=10)
            if response.status_code == 200:
                data = response.json()
                comandos = data.get("comandos", [])
                
                for cmd in comandos:
                    if cmd.get("accion") == "imprimir":
                        cmd_id = cmd.get("id")
                        payload_str = cmd.get("payload")
                        
                        if payload_str:
                            payload = json.loads(payload_str)
                            logger.info(f"📥 Recibido comando de impresión {cmd_id}")
                            
                            # 2. Imprimir localmente
                            if print_ticket_locally(payload):
                                # 3. Confirmar (ACK) al servidor
                                ack_resp = requests.post(f"{API_BASE_URL}/hardware/ack/{cmd_id}", timeout=10)
                                if ack_resp.status_code == 200:
                                    logger.info(f"✅ Comando {cmd_id} marcado como EJECUTADO en el servidor.")
                                else:
                                    logger.error(f"⚠️ Error al hacer ACK del comando {cmd_id}: {ack_resp.text}")
                            else:
                                logger.error(f"⚠️ Se omitió el ACK para {cmd_id} debido a fallo de impresión.")
            else:
                logger.error(f"Error consultando endpoint de polling: HTTP {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"Error de conexión con el servidor (intentando de nuevo en {POLL_INTERVAL}s): {e}")
        except Exception as e:
            logger.error(f"Error inesperado en el poller: {e}")
            
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    poll_and_print()
