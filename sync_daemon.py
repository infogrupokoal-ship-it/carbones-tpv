import logging
import os
import time
import signal
import sys
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Cargar configuración desde .env
load_dotenv()

# Configuración Profesional
VPS_URL = os.environ.get("VPS_URL", "http://localhost:8000") # Default a local si no hay VPS
LOCAL_DB_PATH = os.environ.get("DATABASE_URL", "sqlite:///./tpv_data.sqlite")
LOCAL_PRINTER_URL = os.environ.get("LOCAL_PRINTER_URL", "http://127.0.0.1:8000/webhook/imprimir")
SYNC_INTERVAL = int(os.environ.get("SYNC_INTERVAL", 10))

# Logging con rotación y formato profesional
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [SYNC_DAEMON] %(message)s",
    handlers=[logging.FileHandler("instance/sync.log"), logging.StreamHandler()]
)
logger = logging.getLogger("SyncDaemon")

engine = create_engine(LOCAL_DB_PATH, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

running = True

def handle_exit(signum, frame):
    global running
    logger.info("Recibida señal de parada. Finalizando sincronización de forma segura...")
    running = False

signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)

def push_local_data():
    """Envía pedidos locales nuevos al servidor central."""
    db = SessionLocal()
    try:
        from backend.models import Pedido
        pedidos_unsynced = db.query(Pedido).filter(Pedido.is_synced == False).all()
        
        if not pedidos_unsynced:
            return

        payload = []
        for p in pedidos_unsynced:
            # Serialización simplificada para el ejemplo
            payload.append({
                "id": p.id,
                "numero_ticket": p.numero_ticket,
                "total": p.total,
                "estado": p.estado,
                "fecha": p.fecha.isoformat() if p.fecha else None
            })

        response = requests.post(f"{VPS_URL}/api/sync/push", json={"pedidos": payload}, timeout=10)
        if response.status_code == 200:
            for p in pedidos_unsynced:
                p.is_synced = True
            db.commit()
            logger.info(f"Sincronizados {len(pedidos_unsynced)} pedidos con éxito.")
    except Exception as e:
        logger.error(f"Error en PUSH: {str(e)}")
    finally:
        db.close()

def pull_remote_data():
    """Descarga pedidos o actualizaciones desde la nube."""
    db = SessionLocal()
    try:
        from backend.models import Pedido
        response = requests.get(f"{VPS_URL}/api/sync/pull", timeout=10)
        if response.status_code == 200:
            data = response.json()
            nuevos = data.get("nuevos_pedidos", [])
            for p_dict in nuevos:
                # Verificación de idempotencia (Evitar duplicados ante caída parcial de internet)
                existe = db.query(Pedido).filter_by(id=p_dict.get('id', p_dict['numero_ticket'])).first()
                if existe:
                    logger.info(f"Ticket {p_dict['numero_ticket']} ya procesado antes. Omitiendo.")
                    continue
                    
                logger.info(f"Nuevo pedido de IA WhatsApp recibido! Ticket: {p_dict['numero_ticket']}")
                
                # Insertar en BD Local como YA sincronizado (vino de internet)
                p_local = Pedido(
                    id=p_dict.get('id'), # Usamos el UUID original de la nube si viene
                    numero_ticket=p_dict['numero_ticket'],
                    total=p_dict['total'],
                    origen="WHATSAPP",
                    is_synced=True,
                    estado="PENDIENTE"
                )
                db.add(p_local)
                db.commit()
                
                # Imprimir localmente invocando al puente físico
                try:
                    print_payload = {
                        "tipo": "cocina",
                        "numero_ticket": p_dict['numero_ticket'],
                        "origen": "IA WhatsApp",
                        "total": p_dict['total'],
                        "items": p_dict.get('items', [])
                    }
                    requests.post(LOCAL_PRINTER_URL, json=print_payload, timeout=2)
                except Exception as e:
                    logger.error(f"No se pudo conectar a la impresora local: {e}")
    except Exception as e:
        logger.debug(f"Servidor remoto no disponible: {str(e)}")
    finally:
        db.close()

def pull_hardware_commands():
    """Consulta comandos remotos enviados desde el panel de administración en la nube."""
    try:
        res = requests.get(f"{VPS_URL}/api/hardware/poll", timeout=5)
        if res.status_code == 200:
            data = res.json()
            comandos = data.get("comandos", [])
            for cmd in comandos:
                logger.info(f"Comando remoto recibido: {cmd['accion']} (Origen: {cmd['origen']})")
                if cmd['accion'] == "abrir_caja":
                    # Llamar al puente local
                    try:
                        requests.post("http://127.0.0.1:8000/webhook/abrir_caja", timeout=2)
                        logger.info("=> Cajón abierto localmente con éxito.")
                        # Notificar a la nube (ACK)
                        requests.post(f"{VPS_URL}/api/hardware/ack/{cmd['id']}", timeout=2)
                    except Exception as ex:
                        logger.error(f"=> Error invocando puente local: {ex}")
    except Exception as e:
        logger.debug(f"Error consultando comandos de hardware: {e}")

def daemon_loop():
    logger.info(f"🚀 Demonio de Sincronización iniciado (Target: {VPS_URL})")
    retry_delay = SYNC_INTERVAL
    
    while running:
        try:
            push_local_data()
            pull_remote_data()
            pull_hardware_commands()
            retry_delay = SYNC_INTERVAL # Reset delay on success
        except Exception as e:
            logger.error(f"Fallo crítico en el loop: {e}")
            retry_delay = min(retry_delay * 2, 60) # Backoff hasta 60s
        
        time.sleep(retry_delay)
    
    logger.info("👋 Sync Daemon detenido correctamente.")

if __name__ == "__main__":
    daemon_loop()
