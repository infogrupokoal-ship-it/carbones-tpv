import time
import requests
import json
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os
import threading
import logging

# Configuración
VPS_URL = os.environ.get("VPS_URL", "http://113.30.148.104:5001")
LOCAL_DB_PATH = "sqlite:///./tpv_data.sqlite"
LOCAL_PRINTER_URL = "http://127.0.0.1:8000/webhook/imprimir"
SYNC_INTERVAL = 10 # segundos

logging.basicConfig(level=logging.INFO, format="%(asctime)s [SYNC] %(message)s")

engine = create_engine(LOCAL_DB_PATH, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def push_local_data():
    db = SessionLocal()
    try:
        from models import Pedido
        # Obtener pedidos locales que no han sido subidos
        pedidos_unsynced = db.query(Pedido).filter(Pedido.is_synced == False, Pedido.origen != "WHATSAPP").all()
        
        if not pedidos_unsynced:
            return
            
        payload = []
        for p in pedidos_unsynced:
            items_payload = []
            for it in p.items:
                prod_nombre = it.producto.nombre if it.producto else "Desconocido"
                items_payload.append({
                    "nombre": prod_nombre,
                    "producto_id": it.producto_id,
                    "cantidad": it.cantidad,
                    "precio_unitario": it.precio_unitario
                })
                it.is_synced = True
                
            payload.append({
                "numero_ticket": p.numero_ticket,
                "total": p.total,
                "origen": p.origen,
                "fecha": str(p.fecha),
                "estado": p.estado,
                "cajero_username": p.cajero_username,
                "metodo_pago": p.metodo_pago,
                "descuento_aplicado": p.descuento_aplicado,
                "base_imponible_10": p.base_imponible_10,
                "cuota_iva_10": p.cuota_iva_10,
                "base_imponible_21": p.base_imponible_21,
                "cuota_iva_21": p.cuota_iva_21,
                "items": items_payload
            })
            
        # Intentar Push
        res = requests.post(f"{VPS_URL}/api/sync/push", json={"pedidos": payload}, timeout=5)
        if res.status_code == 200:
            for p in pedidos_unsynced:
                p.is_synced = True
            db.commit()
            logging.info(f"Subidos {len(pedidos_unsynced)} pedidos locales al VPS.")
    except Exception as e:
        # Fallo silencioso si no hay internet
        pass
    finally:
        db.close()

def pull_remote_data():
    db = SessionLocal()
    try:
        from models import Pedido
        res = requests.get(f"{VPS_URL}/api/sync/pull", timeout=5)
        if res.status_code == 200:
            data = res.json()
            nuevos = data.get("nuevos_pedidos", [])
            for p_dict in nuevos:
                # Verificación de idempotencia (Evitar duplicados ante caída parcial de internet)
                existe = db.query(Pedido).filter_by(numero_ticket=p_dict['numero_ticket']).first()
                if existe:
                    logging.info(f"Ticket {p_dict['numero_ticket']} ya procesado antes. Omitiendo.")
                    continue
                    
                logging.info(f"Nuevo pedido de IA WhatsApp recibido! Ticket: {p_dict['numero_ticket']}")
                
                # Insertar en BD Local como YA sincronizado (vino de internet)
                p_local = Pedido(
                    numero_ticket=p_dict['numero_ticket'],
                    total=p_dict['total'],
                    origen="WHATSAPP",
                    is_synced=True,
                    estado="PENDIENTE"
                )
                db.add(p_local)
                db.commit()
                
                # Imprimir localmente invocando al puente físico!
                try:
                    print_payload = {
                        "tipo": "cocina",
                        "numero_ticket": p_dict['numero_ticket'],
                        "origen": "IA WhatsApp",
                        "total": p_dict['total'],
                        "items": p_dict.get('items', [])
                    }
                    requests.post(LOCAL_PRINTER_URL, json=print_payload, timeout=2)
                except:
                    logging.error("No se pudo conectar a la impresora local (puerto 8000)")
                    
    except Exception as e:
        pass
    finally:
        db.close()

def daemon_loop():
    logging.info(f"Iniciando Demonio de Sincronización...")
    logging.info(f"Conectando contra VPS en: {VPS_URL}")
    while True:
        push_local_data()
        pull_remote_data()
        time.sleep(SYNC_INTERVAL)

if __name__ == "__main__":
    daemon_loop()
