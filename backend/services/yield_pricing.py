import asyncio
from backend.database import SessionLocal
from backend.models import Producto, YieldRule
from backend.utils.logger import logger

class YieldPricingService:
    """
    Yield Pricing Service V9.3.
    Ajusta precios de productos dinámicamente según reglas activas.
    """
    
    @staticmethod
    async def process_prices():
        while True:
            db = SessionLocal()
            try:
                # 1. Buscar regla de Yield activa (prioridad alta)
                active_rule = db.query(YieldRule).filter(YieldRule.is_active == True).first()
                
                if active_rule:
                    multiplier = 1.0 + (active_rule.ajuste_precio_pct / 100)
                    logger.info(f"[YIELD] Aplicando multiplicador x{multiplier} ({active_rule.nombre})")
                    
                    # 2. Actualizar productos (solo si tienen precio_base definido)
                    db.query(Producto).filter(Producto.precio_base != None).update({
                        "precio": Producto.precio_base * multiplier
                    }, synchronize_session=False)
                    
                    db.commit()
                else:
                    # Resetear a precio base
                    db.query(Producto).filter(Producto.precio_base != None).update({
                        "precio": Producto.precio_base
                    }, synchronize_session=False)
                    db.commit()
                    
            except Exception as e:
                logger.error(f"[YIELD] Error en ajuste: {e}")
            finally:
                db.close()
                
            await asyncio.sleep(300) # Ajuste cada 5 minutos

yield_engine = YieldPricingService()
