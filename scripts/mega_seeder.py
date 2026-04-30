import uuid
from backend.database import SessionLocal, Base, engine
from backend.models import Categoria, Producto, Ingrediente, Proveedor, Usuario
from backend.utils.auth import get_password_hash

def seed_professional_data():
    db = SessionLocal()
    
    # 0. Limpiar (Opcional, para desarrollo limpio)
    # Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # 1. Proveedores
    prov_central = Proveedor(id=str(uuid.uuid4()), nombre="Avícola Central SL", email="pedidos@avicola.es")
    prov_bebidas = Proveedor(id=str(uuid.uuid4()), nombre="Distribuciones Bebi", email="ventas@bebi.com")
    db.add_all([prov_central, prov_bebidas])
    db.commit()

    # 2. Categorías
    cat_asados = Categoria(id=str(uuid.uuid4()), nombre="Asados", color="#ff5722")
    cat_bebidas = Categoria(id=str(uuid.uuid4()), nombre="Bebidas", color="#2196f3")
    cat_guarniciones = Categoria(id=str(uuid.uuid4()), nombre="Guarniciones", color="#4caf50")
    db.add_all([cat_asados, cat_bebidas, cat_guarniciones])
    db.commit()

    # 3. Productos
    productos = [
        Producto(id=str(uuid.uuid4()), nombre="Pollo Asado Entero", precio=12.50, categoria_id=cat_asados.id, stock_actual=20),
        Producto(id=str(uuid.uuid4()), nombre="Medio Pollo Asado", precio=7.00, categoria_id=cat_asados.id, stock_actual=15),
        Producto(id=str(uuid.uuid4()), nombre="Patatas Fritas (Ración)", precio=3.50, categoria_id=cat_guarniciones.id, stock_actual=50),
        Producto(id=str(uuid.uuid4()), nombre="Refresco 33cl", precio=2.00, categoria_id=cat_bebidas.id, stock_actual=100),
        Producto(id=str(uuid.uuid4()), nombre="Cerveza Especial", precio=2.50, categoria_id=cat_bebidas.id, stock_actual=80)
    ]
    db.add_all(productos)

    # 4. Ingredientes (Materia Prima)
    ingredientes = [
        Ingrediente(id=str(uuid.uuid4()), nombre="Pollo Fresco", stock_actual=50, stock_minimo=10, unidad_medida="unidades", proveedor_id=prov_central.id),
        Ingrediente(id=str(uuid.uuid4()), nombre="Aceite de Girasol", stock_actual=25, stock_minimo=5, unidad_medida="litros", proveedor_id=prov_central.id),
        Ingrediente(id=str(uuid.uuid4()), nombre="Patata Agria", stock_actual=100, stock_minimo=20, unidad_medida="kg", proveedor_id=prov_central.id)
    ]
    db.add_all(ingredientes)

    # 5. Usuarios (Seguridad)
    usuarios = [
        Usuario(id=str(uuid.uuid4()), username="admin", pin_hash=get_password_hash("1234"), rol="admin"),
        Usuario(id=str(uuid.uuid4()), username="caja1", pin_hash=get_password_hash("0000"), rol="staff"),
        Usuario(id=str(uuid.uuid4()), username="cocina", pin_hash=get_password_hash("1111"), rol="staff")
    ]
    db.add_all(usuarios)

    db.commit()
    print("✅ Ecosistema de Datos Profesionales Sembrado con Éxito.")
    db.close()

if __name__ == "__main__":
    seed_professional_data()
