from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Ingrediente, Proveedor

DB_PATH = "sqlite:///tpv_data.sqlite"
engine = create_engine(DB_PATH, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def seed_inventario():
    db = SessionLocal()
    try:
        if not db.query(Proveedor).first():
            print("Seeding proveedores e ingredientes...")

            p1 = Proveedor(
                nombre="Makro",
                telefono="600123456",
                email="pedidos@makro.es",
                dias_entrega="Lunes, Jueves",
            )
            p2 = Proveedor(
                nombre="Cárnicas López",
                telefono="600987654",
                email="pedidos@carnicaslopez.com",
                dias_entrega="Martes, Viernes",
            )
            p3 = Proveedor(
                nombre="Frutas Paco",
                telefono="600111222",
                email="paco@frutaspaco.es",
                dias_entrega="Lunes, Miercoles, Viernes",
            )
            p4 = Proveedor(
                nombre="Bebidas del Turia",
                telefono="600333444",
                email="info@bebidasdelturia.com",
                dias_entrega="Martes",
            )

            db.add_all([p1, p2, p3, p4])
            db.flush()

            ingredientes = [
                Ingrediente(
                    nombre="Pollo Fresco (Cajas)",
                    unidad_medida="Caja (10 ud)",
                    stock_actual=5,
                    stock_minimo=3,
                    coste_unitario=35.0,
                    proveedor_id=p2.id,
                ),
                Ingrediente(
                    nombre="Arroz Bomba",
                    unidad_medida="Saco (5 Kg)",
                    stock_actual=2,
                    stock_minimo=4,
                    coste_unitario=12.5,
                    proveedor_id=p1.id,
                ),
                Ingrediente(
                    nombre="Patatas Caseras",
                    unidad_medida="Saco (10 Kg)",
                    stock_actual=10,
                    stock_minimo=5,
                    coste_unitario=8.0,
                    proveedor_id=p3.id,
                ),
                Ingrediente(
                    nombre="Aceite Girasol Alto Rendimiento",
                    unidad_medida="Garrafa (5 L)",
                    stock_actual=2,
                    stock_minimo=5,
                    coste_unitario=15.0,
                    proveedor_id=p1.id,
                ),
                Ingrediente(
                    nombre="Codillos Pre-cocinados",
                    unidad_medida="Caja (20 ud)",
                    stock_actual=3,
                    stock_minimo=3,
                    coste_unitario=60.0,
                    proveedor_id=p2.id,
                ),
                Ingrediente(
                    nombre="Refrescos Lata (Surtido)",
                    unidad_medida="Pack (24 ud)",
                    stock_actual=10,
                    stock_minimo=15,
                    coste_unitario=10.0,
                    proveedor_id=p4.id,
                ),
                Ingrediente(
                    nombre="Pan de Bocadillo",
                    unidad_medida="Caja (50 ud)",
                    stock_actual=2,
                    stock_minimo=3,
                    coste_unitario=18.0,
                    proveedor_id=p1.id,
                ),
                Ingrediente(
                    nombre="Leña de Carrasca",
                    unidad_medida="Saca (500 Kg)",
                    stock_actual=1,
                    stock_minimo=1,
                    coste_unitario=80.0,
                    proveedor_id=p1.id,
                ),
            ]

            db.add_all(ingredientes)
            db.commit()
            print("Inventario inyectado con éxito.")
        else:
            print("Inventario ya estaba inyectado.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding inventario: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_inventario()
