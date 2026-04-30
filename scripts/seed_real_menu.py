from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.models import Categoria, Producto

DB_PATH = "sqlite:///tpv_data.sqlite"
engine = create_engine(DB_PATH, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def seed():
    db = SessionLocal()
    try:
        # Borrar categorias de prueba de la noche
        db.query(Producto).filter(Producto.precio == 4.50).delete(
            synchronize_session=False
        )  # delete dummy

        cats = [
            ("Bocadillos y Chivitos", 4),
            ("Brascadas", 5),
            ("Especiales de la Casa", 6),
            ("Del Mar", 7),
            ("Bocadillos Clásicos", 8),
            ("Bebidas Noche", 9),
        ]

        cat_map = {}
        for c_name, order in cats:
            cat = db.query(Categoria).filter(Categoria.nombre == c_name).first()
            if not cat:
                cat = Categoria(nombre=c_name, orden=order)
                db.add(cat)
                db.flush()
            cat_map[c_name] = cat.id

        products = [
            # Bocadillos y Chivitos
            (
                "Chivito de Pollo",
                6.50,
                "Bocadillos y Chivitos",
                "Mayonesa, tomate, cebolla, lechuga, pechuga de pollo, queso y bacon",
            ),
            ("Chivito de Lomo", 6.50, "Bocadillos y Chivitos", ""),
            ("Chivito de Ternera", 7.00, "Bocadillos y Chivitos", ""),
            ("Chivito de Carne de Caballo", 8.00, "Bocadillos y Chivitos", ""),
            ("Lomo, Queso y Bacon", 6.50, "Bocadillos y Chivitos", ""),
            ("Bocadillo de Hamburguesa Completa", 5.50, "Bocadillos y Chivitos", ""),
            # Brascadas
            (
                "Brascada",
                6.50,
                "Brascadas",
                "Mayonesa, tomate, cebolla plancha, ternera y jamon serrano",
            ),
            ("Brascada de Lomo", 5.50, "Brascadas", ""),
            ("Brascada de Caballo", 7.00, "Brascadas", ""),
            # Especiales de la Casa
            (
                "Bocadillo Caramelizado La Granja",
                7.50,
                "Especiales de la Casa",
                "Cebolla caramelizada, queso de cabra, pechuga de pollo, queso, bacon y jamon serrano",
            ),
            ("Sobrasada, Lomo, queso y bacon", 5.00, "Especiales de la Casa", ""),
            (
                "Lomo, pimientos, cebolla a la plancha",
                5.00,
                "Especiales de la Casa",
                "",
            ),
            # Del Mar
            ("Bocadillo de Sepia a la plancha con mayonesa", 8.00, "Del Mar", ""),
            ("Calamares con Alioli", 8.00, "Del Mar", ""),
            ("Revuelto de gambas con ajos tiernos", 8.00, "Del Mar", ""),
            ("Tomate, anchoas y queso", 6.00, "Del Mar", ""),
            # Bocadillos Clásicos
            (
                "Bocadillo Vegetal",
                5.50,
                "Bocadillos Clásicos",
                "Mayonesa, tomate, cebolla, lechuga, atun, huevo duro, maiz y esparragos",
            ),
            ("Tortilla de patatas con alioli", 5.50, "Bocadillos Clásicos", ""),
            ("Tortilla Francesa, tomate y longanizas", 5.00, "Bocadillos Clásicos", ""),
            ("Embutidos con pisto", 5.50, "Bocadillos Clásicos", ""),
            (
                "Pechuga Empanada",
                5.50,
                "Bocadillos Clásicos",
                "Pechuga, mayonesa, queso, bacon y patatas",
            ),
            (
                "Huevos fritos, chistorra, patatas y alioli",
                5.50,
                "Bocadillos Clásicos",
                "",
            ),
            # Bebidas adicionales
            ("Bebida / Refresco", 1.80, "Bebidas Noche", ""),
            ("Litro de Cerveza", 2.50, "Bebidas Noche", ""),
            ("Litro de Refresco", 1.50, "Bebidas Noche", ""),
        ]

        for name, price, c_name, desc in products:
            p = db.query(Producto).filter(Producto.nombre == name).first()
            if not p:
                p = Producto(
                    nombre=name,
                    precio=price,
                    categoria_id=cat_map[c_name],
                    descripcion=desc,
                    stock_actual=50,
                )  # Stock inicial alto
                db.add(p)

        # Eliminar posible dummy antiguo si se llamo turno noche generico
        cat_old = db.query(Categoria).filter(Categoria.nombre == "Turno Noche").first()
        if cat_old:
            db.query(Producto).filter(Producto.categoria_id == cat_old.id).delete(
                synchronize_session=False
            )
            db.delete(cat_old)

        db.commit()
        print("Real Night Menu Seeded!")
    except Exception as e:
        print("Error:", e)
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed()
