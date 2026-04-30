from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.models import Categoria, Producto

DB_PATH = "sqlite:///tpv_data.sqlite"
engine = create_engine(DB_PATH, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def seed_night_menu():
    db = SessionLocal()
    try:
        # Categorías del Turno Noche (Orden >= 10 para separarlas del Turno Mañana)
        categorias_data = [
            {"nombre": "BOCADILLOS Y CHIVITOS", "orden": 10},
            {"nombre": "BRASCADAS", "orden": 11},
            {"nombre": "ESPECIALES DE LA CASA", "orden": 12},
            {"nombre": "DEL MAR", "orden": 13},
            {"nombre": "BOCADILLOS CLÁSICOS", "orden": 14},
        ]

        cat_objs = {}
        for cdata in categorias_data:
            cat = (
                db.query(Categoria).filter(Categoria.nombre == cdata["nombre"]).first()
            )
            if not cat:
                cat = Categoria(nombre=cdata["nombre"], orden=cdata["orden"])
                db.add(cat)
                db.flush()
            cat_objs[cdata["nombre"]] = cat

        # Productos
        productos_data = [
            # BOCADILLOS Y CHIVITOS
            {
                "nombre": "Chivito de Pollo",
                "desc": "Mayonesa, tomate, cebolla, lechuga, pechuga de pollo, queso y bacon",
                "precio": 6.50,
                "cat": "BOCADILLOS Y CHIVITOS",
            },
            {
                "nombre": "Chivito de Lomo",
                "desc": "Mayonesa, tomate, cebolla, lechuga, lomo, queso y bacon",
                "precio": 6.50,
                "cat": "BOCADILLOS Y CHIVITOS",
            },
            {
                "nombre": "Chivito de Ternera",
                "desc": "Mayonesa, tomate, cebolla, lechuga, ternera, queso y bacon",
                "precio": 7.00,
                "cat": "BOCADILLOS Y CHIVITOS",
            },
            {
                "nombre": "Chivito de Carne de Caballo",
                "desc": "Mayonesa, tomate, cebolla, lechuga, carne de caballo, queso y bacon",
                "precio": 8.00,
                "cat": "BOCADILLOS Y CHIVITOS",
            },
            {
                "nombre": "Lomo, Queso y Bacon",
                "desc": "Lomo, queso y bacon",
                "precio": 6.50,
                "cat": "BOCADILLOS Y CHIVITOS",
            },
            {
                "nombre": "Bocadillo de Hamburguesa Completa",
                "desc": "Hamburguesa completa",
                "precio": 5.50,
                "cat": "BOCADILLOS Y CHIVITOS",
            },
            # BRASCADAS
            {
                "nombre": "Brascada",
                "desc": "Mayonesa, tomate, cebolla plancha, ternera y jamón serrano",
                "precio": 6.50,
                "cat": "BRASCADAS",
            },
            {
                "nombre": "Brascada de Lomo",
                "desc": "Mayonesa, tomate, cebolla plancha, lomo y jamón serrano",
                "precio": 5.50,
                "cat": "BRASCADAS",
            },
            {
                "nombre": "Brascada de Caballo",
                "desc": "Mayonesa, tomate, cebolla plancha, carne de caballo y jamón serrano",
                "precio": 7.00,
                "cat": "BRASCADAS",
            },
            # ESPECIALES DE LA CASA
            {
                "nombre": "Bocadillo Cabramelizado La Granja",
                "desc": "Cebolla caramelizada, queso de cabra, pechuga de pollo, queso, bacon y jamón serrano",
                "precio": 7.50,
                "cat": "ESPECIALES DE LA CASA",
            },
            {
                "nombre": "Sobrasada",
                "desc": "Lomo, queso y bacon (Nota: ver ingredientes reales de sobrasada si los hay)",
                "precio": 5.00,
                "cat": "ESPECIALES DE LA CASA",
            },
            {
                "nombre": "Lomo, Pimientos, Cebolla a la plancha",
                "desc": "Lomo, pimientos y cebolla",
                "precio": 5.00,
                "cat": "ESPECIALES DE LA CASA",
            },
            # DEL MAR
            {
                "nombre": "Bocadillo de Sepia a la plancha con Mayonesa",
                "desc": "Sepia a la plancha y mayonesa",
                "precio": 8.00,
                "cat": "DEL MAR",
            },
            {
                "nombre": "Calamares con Alioli",
                "desc": "Calamares y alioli",
                "precio": 8.00,
                "cat": "DEL MAR",
            },
            {
                "nombre": "Revuelto de Gambas con Ajos Tiernos",
                "desc": "Gambas y ajos tiernos",
                "precio": 8.00,
                "cat": "DEL MAR",
            },
            {
                "nombre": "Tomate, Anchoas y Queso",
                "desc": "Tomate, anchoas y queso fresco",
                "precio": 6.00,
                "cat": "DEL MAR",
            },
            # BOCADILLOS CLÁSICOS
            {
                "nombre": "Bocadillo Vegetal",
                "desc": "Mayonesa, tomate, cebolla, lechuga, atún, huevo duro, maíz y espárragos",
                "precio": 5.50,
                "cat": "BOCADILLOS CLÁSICOS",
            },
            {
                "nombre": "Tortilla de Patatas con Alioli",
                "desc": "Tortilla de patatas casera y alioli",
                "precio": 5.50,
                "cat": "BOCADILLOS CLÁSICOS",
            },
            {
                "nombre": "Tortilla Francesa, Tomate y Longanizas",
                "desc": "Tortilla francesa, tomate y longanizas",
                "precio": 5.00,
                "cat": "BOCADILLOS CLÁSICOS",
            },
            {
                "nombre": "Embutidos con Pisto",
                "desc": "Embutidos variados con pisto manchego",
                "precio": 5.50,
                "cat": "BOCADILLOS CLÁSICOS",
            },
            {
                "nombre": "Pechuga Empanada",
                "desc": "Pechuga, mayonesa, queso, bacon y patatas",
                "precio": 5.50,
                "cat": "BOCADILLOS CLÁSICOS",
            },
            {
                "nombre": "Huevos Fritos, Chistorra, Patatas y Alioli",
                "desc": "Huevos fritos, chistorra, patatas y alioli",
                "precio": 5.50,
                "cat": "BOCADILLOS CLÁSICOS",
            },
        ]

        for pdata in productos_data:
            cat_id = cat_objs[pdata["cat"]].id
            prod = db.query(Producto).filter(Producto.nombre == pdata["nombre"]).first()
            if not prod:
                prod = Producto(
                    nombre=pdata["nombre"],
                    descripcion=pdata["desc"],
                    precio=pdata["precio"],
                    categoria_id=cat_id,
                    stock_actual=50,  # Ponemos 50 de stock base para que se puedan vender
                )
                db.add(prod)

        db.commit()
        print("✅ Menú nocturno inyectado con éxito en la base de datos.")
    except Exception as e:
        print(f"❌ Error al inyectar menú nocturno: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_night_menu()
