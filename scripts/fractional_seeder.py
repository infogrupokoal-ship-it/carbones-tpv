from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base, Categoria, Producto, Usuario

DB_PATH = "sqlite:///tpv_data.sqlite"
engine = create_engine(DB_PATH, connect_args={"check_same_thread": False})
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def seed():
    db = SessionLocal()
    try:
        if not db.query(Usuario).first():
            db.add_all(
                [
                    Usuario(username="encargado_mañana", password="123", rol="MANANA"),
                    Usuario(username="encargado_tarde", password="123", rol="TARDE"),
                    Usuario(username="admin", password="123", rol="ADMIN"),
                ]
            )
            db.flush()

        cat1 = db.query(Categoria).filter(Categoria.nombre == "Pollos Asados").first()
        if not cat1:
            cat1 = Categoria(nombre="Pollos Asados", orden=1)
            cat2 = Categoria(nombre="Guarniciones", orden=2)
            cat3 = Categoria(nombre="Bebidas", orden=3)
            # Nocturnos
            cat4 = Categoria(nombre="Bocadillos y Chivitos", orden=4)
            cat5 = Categoria(nombre="Brascadas", orden=5)
            cat6 = Categoria(nombre="Especiales de la Casa", orden=6)
            cat7 = Categoria(nombre="Del Mar", orden=7)
            cat8 = Categoria(nombre="Bocadillos Clásicos", orden=8)
            cat9 = Categoria(nombre="Bebidas Noche", orden=9)

            db.add_all([cat1, cat2, cat3, cat4, cat5, cat6, cat7, cat8, cat9])
            db.flush()

            # --- PRODUCTOS NORMALES ---
            prod3 = Producto(
                nombre="Patatas Fritas",
                precio=3.00,
                categoria_id=cat2.id,
                stock_actual=50,
            )
            prod4 = Producto(
                nombre="Croquetas", precio=1.00, categoria_id=cat2.id, stock_actual=100
            )
            prod5 = Producto(
                nombre="Refresco Cola",
                precio=1.50,
                categoria_id=cat3.id,
                stock_actual=200,
            )
            db.add_all([prod3, prod4, prod5])

            # --- LOGICA FRACCIONAL DEL POLLO ---
            # Pollo invisible base (Unidad minima = 1 Cuarto)
            pollo_base = Producto(
                nombre="[MATERIA] Pollo Base",
                precio=0,
                categoria_id=None,
                is_active=False,
                stock_actual=100,
            )  # 100 cuartos = 25 pollos enteros
            db.add(pollo_base)
            db.flush()

            # Sub-productos (Los factors son cuartos: 4 cuartos = 1 entero, 2 cuartos = 1 medio, 1 cuarto = cuarto)
            p_entero = Producto(
                nombre="Pollo Entero",
                precio=10.00,
                categoria_id=cat1.id,
                stock_base_id=pollo_base.id,
                factor_stock=4,
            )
            p_medio = Producto(
                nombre="Medio Pollo",
                precio=5.50,
                categoria_id=cat1.id,
                stock_base_id=pollo_base.id,
                factor_stock=2,
            )
            p_cuarto = Producto(
                nombre="Cuarto de Pollo",
                precio=3.00,
                categoria_id=cat1.id,
                stock_base_id=pollo_base.id,
                factor_stock=1,
            )
            db.add_all([p_entero, p_medio, p_cuarto])

            db.commit()
            print("Fractional and user mapping seeded correctly!")
        else:
            print("Already seeded.")
    except Exception as e:
        db.rollback()
        print("Error seeding:", e)
    finally:
        db.close()


if __name__ == "__main__":
    seed()
