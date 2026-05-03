import uuid
from backend.database import SessionLocal, engine
from backend.models import Categoria, Producto, Base

def seed_industrial_ultra():
    print("🚀 Iniciando Seeding Industrial ULTRA v2.1.2...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        # 1. Limpiar datos previos si existen (Opcional, para asegurar consistencia)
        # db.query(Producto).delete()
        # db.query(Categoria).delete()
        
        if db.query(Categoria).count() > 0:
            print("⚠️ La base de datos ya contiene datos. Saltando seeding para evitar duplicados.")
            return

        # 2. Categorías Gourmet
        cats = {
            "POLLOS": Categoria(id=str(uuid.uuid4()), nombre="Pollos al Carbón"),
            "ENTRANTES": Categoria(id=str(uuid.uuid4()), nombre="Entrantes Gourmet"),
            "BEBIDAS": Categoria(id=str(uuid.uuid4()), nombre="Bebidas & Bodega"),
            "POSTRES": Categoria(id=str(uuid.uuid4()), nombre="Postres Artesanos")
        }
        db.add_all(cats.values())
        db.commit()

        # 3. Productos de Élite
        productos = [
            # Pollos
            Producto(
                id=str(uuid.uuid4()),
                nombre="Pollo al Carbón Premium",
                descripcion="Nuestro pollo icónico marinado 24h con especias secretas y asado con leña de encina.",
                precio=14.50,
                categoria_id=cats["POLLOS"].id,
                stock_actual=50,
                url_imagen="https://images.unsplash.com/photo-1598103442097-8b74394b95c6?auto=format&fit=crop&q=80&w=800",
                is_active=True
            ),
            Producto(
                id=str(uuid.uuid4()),
                nombre="Medio Pollo Gourmet",
                descripcion="Ración perfecta para uno, acompañada de su jugo natural y aroma a humo.",
                precio=8.50,
                categoria_id=cats["POLLOS"].id,
                stock_actual=100,
                url_imagen="https://images.unsplash.com/photo-1626082927389-6cd097cdc6ec?auto=format&fit=crop&q=80&w=800",
                is_active=True
            ),
            # Entrantes
            Producto(
                id=str(uuid.uuid4()),
                nombre="Patatas Braseadas Triple Cocción",
                descripcion="Crujientes por fuera, cremosas por dentro. Con nuestra salsa brava de autor.",
                precio=5.90,
                categoria_id=cats["ENTRANTES"].id,
                stock_actual=200,
                url_imagen="https://images.unsplash.com/photo-1518013391915-e44359403868?auto=format&fit=crop&q=80&w=800",
                is_active=True
            ),
            Producto(
                id=str(uuid.uuid4()),
                nombre="Croquetas de Pollo a la Brasa (6u)",
                descripcion="Bechamel sedosa con trozos de nuestro pollo al carbón. Puro sabor.",
                precio=7.50,
                categoria_id=cats["ENTRANTES"].id,
                stock_actual=150,
                url_imagen="https://images.unsplash.com/photo-1626082896492-766af4eb6501?auto=format&fit=crop&q=80&w=800",
                is_active=True
            ),
            # Bebidas
            Producto(
                id=str(uuid.uuid4()),
                nombre="Cerveza Artesana 'El Fuego'",
                descripcion="Lager premium local, filtrada en frío, ideal para maridar con carnes asadas.",
                precio=3.80,
                categoria_id=cats["BEBIDAS"].id,
                stock_actual=300,
                url_imagen="https://images.unsplash.com/photo-1535958636474-b021ee887b13?auto=format&fit=crop&q=80&w=800",
                is_active=True
            ),
            Producto(
                id=str(uuid.uuid4()),
                nombre="Vino Tinto Crianza D.O.",
                descripcion="Selección de la bodega para realzar los matices del ahumado.",
                precio=18.00,
                categoria_id=cats["BEBIDAS"].id,
                stock_actual=40,
                url_imagen="https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?auto=format&fit=crop&q=80&w=800",
                is_active=True
            )
        ]
        db.add_all(productos)
        db.commit()
        print(f"✅ Seeding completado: {len(productos)} productos y {len(cats)} categorías inyectadas.")

    except Exception as e:
        db.rollback()
        print(f"❌ Error durante el seeding: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_industrial_ultra()
