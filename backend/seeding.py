import uuid
import logging
from sqlalchemy.orm import Session
from .database import SessionLocal, engine
from .models import Categoria, Producto, Base

logger = logging.getLogger(__name__)

def run_auto_seeding():
    """
    Motor de Sincronización de Datos Industrial.
    Garantiza que la base de datos de producción tenga el catálogo gourmet v2.1.2.
    """
    db = SessionLocal()
    try:
        if db.query(Categoria).count() > 0:
            return

        logger.info("🚚 Iniciando Inyección de Datos Gourmet (v2.1.2)...")
        
        # Categorías
        cats = {
            "POLLOS": Categoria(id=str(uuid.uuid4()), nombre="Pollos al Carbón"),
            "ENTRANTES": Categoria(id=str(uuid.uuid4()), nombre="Entrantes Gourmet"),
            "BEBIDAS": Categoria(id=str(uuid.uuid4()), nombre="Bebidas & Bodega"),
            "POSTRES": Categoria(id=str(uuid.uuid4()), nombre="Postres Artesanos")
        }
        db.add_all(cats.values())
        db.commit()

        # Productos
        productos = [
            Producto(
                id=str(uuid.uuid4()),
                nombre="Pollo al Carbón Premium",
                descripcion="Braseado con leña de encina y marinado 24h.",
                precio=14.50,
                categoria_id=cats["POLLOS"].id,
                stock_actual=50,
                url_imagen="https://images.unsplash.com/photo-1598103442097-8b74394b95c6?auto=format&fit=crop&q=80&w=800",
                is_active=True
            ),
            Producto(
                id=str(uuid.uuid4()),
                nombre="Patatas Braseadas",
                descripcion="Triple cocción con salsa brava de autor.",
                precio=5.90,
                categoria_id=cats["ENTRANTES"].id,
                stock_actual=100,
                url_imagen="https://images.unsplash.com/photo-1518013391915-e44359403868?auto=format&fit=crop&q=80&w=800",
                is_active=True
            ),
            Producto(
                id=str(uuid.uuid4()),
                nombre="Cerveza Artesana",
                descripcion="Lager premium local filtrada en frío.",
                precio=3.80,
                categoria_id=cats["BEBIDAS"].id,
                stock_actual=200,
                url_imagen="https://images.unsplash.com/photo-1535958636474-b021ee887b13?auto=format&fit=crop&q=80&w=800",
                is_active=True
            )
        ]
        db.add_all(productos)
        db.commit()
        logger.info(f"✅ Catálogo industrial inyectado con éxito.")
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Fallo en Auto-Seeding: {e}")
    finally:
        db.close()
