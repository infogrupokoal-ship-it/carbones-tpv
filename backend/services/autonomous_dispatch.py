import asyncio
import random
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models import Pedido, Usuario
from backend.utils.logger import logger

class AutonomousDispatch:
    """
    Servicio Autónomo de Despacho V9.3.
    Asigna pedidos de forma inteligente a repartidores disponibles.
    """
    
    @staticmethod
    async def run_cycle():
        """Bucle infinito de despacho autónomo."""
        while True:
            db = SessionLocal()
            try:
                # 1. Buscar pedidos pendientes de reparto
                pending_orders = db.query(Pedido).filter(
                    Pedido.metodo_envio == "DOMICILIO",
                    Pedido.estado == "PREPARADO"
                ).all()
                
                if pending_orders:
                    # 2. Buscar repartidores disponibles (con rol REPARTIDOR)
                    drivers = db.query(Usuario).filter(Usuario.role == "REPARTIDOR").all()
                    
                    if drivers:
                        for order in pending_orders:
                            driver = random.choice(drivers) # Algoritmo de asignación estocástica (mejorable a distancia)
                            order.estado = "EN_REPARTO"
                            order.repartidor_id = driver.id
                            logger.info(f"[DISPATCH] Pedido {order.numero_ticket} asignado a {driver.username}")
                        
                        db.commit()
                
            except Exception as e:
                logger.error(f"[DISPATCH] Error en ciclo: {e}")
            finally:
                db.close()
                
            await asyncio.sleep(30) # Ciclo de 30 segundos

dispatcher = AutonomousDispatch()
