import uuid
from backend.database import SessionLocal, Base, engine
from backend.models import Categoria, Producto, Usuario, Tienda, Ingrediente, Proveedor
from backend.utils.auth import get_password_hash
from backend.utils.logger import logger

def seed_ultra_industrial():
    print("🚀 Iniciando Sembrado ULTRA INDUSTRIAL...")
    db = SessionLocal()
    
    try:
        # 1. Crear Tienda Central (Base del Multi-tenancy)
        tienda = db.query(Tienda).filter_by(nombre="Carbones y Pollos Central").first()
        if not tienda:
            tienda = Tienda(
                id=str(uuid.uuid4()),
                nombre="Carbones y Pollos Central",
                direccion="Av. del Fuego, 123",
                telefono="900-KOAL-TPV"
            )
            db.add(tienda)
            db.commit()
            print(f"✅ Tienda Central creada: {tienda.id}")

        # 2. Usuarios de Alta Jerarquía
        if not db.query(Usuario).filter_by(username="admin").first():
            admin = Usuario(
                id=str(uuid.uuid4()),
                username="admin",
                full_name="Administrador de Sistema",
                pin_hash=get_password_hash("1234"),
                rol="ADMIN",
                tienda_id=tienda.id
            )
            db.add(admin)
            print("✅ Usuario ADMIN creado (PIN: 1234)")

        # 3. Proveedores Estratégicos
        p_avicola = Proveedor(id=str(uuid.uuid4()), nombre="Avícola Galega S.A.", email="pedidos@avicola.es")
        p_bebidas = Proveedor(id=str(uuid.uuid4()), nombre="Bebidas del Sur", email="logistica@bebidas.com")
        db.add_all([p_avicola, p_bebidas])
        db.commit()

        # 4. Categorías Profesionales
        categorias = {
            "pollos": Categoria(id=str(uuid.uuid4()), nombre="Pollos Asados"),
            "combos": Categoria(id=str(uuid.uuid4()), nombre="Combos Familiares"),
            "bebidas": Categoria(id=str(uuid.uuid4()), nombre="Bebidas y Refrescos"),
            "postres": Categoria(id=str(uuid.uuid4()), nombre="Postres Artesanos")
        }
        db.add_all(categorias.values())
        db.commit()

        # 5. Catálogo de Productos con Imágenes Reales (Unsplash fallback)
        productos = [
            Producto(
                id=str(uuid.uuid4()),
                nombre="Pollo al Carbón (Entero)",
                descripcion="Pollo de corral marinado 24h y asado a fuego lento.",
                precio=14.90,
                categoria_id=categorias["pollos"].id,
                tienda_id=tienda.id,
                stock_actual=100,
                imagen_url="https://images.unsplash.com/photo-1598103442097-8b74394b95c6?auto=format&fit=crop&q=80&w=600"
            ),
            Producto(
                id=str(uuid.uuid4()),
                nombre="Medio Pollo + Patatas",
                descripcion="Ideal para una persona. Incluye ración de patatas fritas.",
                precio=9.50,
                categoria_id=categorias["pollos"].id,
                tienda_id=tienda.id,
                stock_actual=150,
                imagen_url="https://images.unsplash.com/photo-1626082927389-6cd097cdc6ec?auto=format&fit=crop&q=80&w=600"
            ),
            Producto(
                id=str(uuid.uuid4()),
                nombre="Combo Familiar XL",
                descripcion="2 Pollos enteros + 2 Raciones de Patatas + Bebida 2L.",
                precio=34.90,
                categoria_id=categorias["combos"].id,
                tienda_id=tienda.id,
                stock_actual=50,
                imagen_url="https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&q=80&w=600"
            ),
            Producto(
                id=str(uuid.uuid4()),
                nombre="Cerveza Artesana Koal",
                descripcion="Refrescante y lupulada, ideal para carnes asadas.",
                precio=3.50,
                categoria_id=categorias["bebidas"].id,
                tienda_id=tienda.id,
                stock_actual=200,
                imagen_url="https://images.unsplash.com/photo-1535958636474-b021ee887b13?auto=format&fit=crop&q=80&w=600"
            )
        ]
        db.add_all(productos)
        db.commit()

        # 6. Materia Prima (Ingredientes)
        ing_pollo = Ingrediente(id=str(uuid.uuid4()), nombre="Pollo Crudo (kg)", stock_actual=200, stock_minimo=40, unidad_medida="kg", proveedor_id=p_avicola.id)
        db.add(ing_pollo)
        db.commit()

        print("🚀 [SUCCESS] Sistema ULTRA INDUSTRIAL sembrado correctamente.")

    except Exception as e:
        db.rollback()
        print(f"❌ [ERROR] Fallo en el sembrado: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_ultra_industrial()
