from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.models import Categoria, Producto

DB_PATH = "sqlite:///tpv_data.sqlite"
engine = create_engine(DB_PATH, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def seed_night_menu_image():
    db = SessionLocal()
    try:
        # Categorías del Turno Noche (Orden >= 10)
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
                cat = Categoria(nombre=cdata["nombre"])
                db.add(cat)
                db.flush()
            cat_objs[cdata["nombre"]] = cat

        productos_data = [
            # BOCADILLOS Y CHIVITOS
            {
                "nombre": "CHIVITO DE POLLO",
                "desc": "Mayonesa, tomate, cebolla, lechuga, pechuga de pollo, queso fundido y bacon crujiente",
                "precio": 6.50,
                "cat": "BOCADILLOS Y CHIVITOS",
            },
            {
                "nombre": "CHIVITO DE LOMO",
                "desc": "Mayonesa, tomate, cebolla, lechuga, lomo fresco, queso y bacon",
                "precio": 6.50,
                "cat": "BOCADILLOS Y CHIVITOS",
            },
            {
                "nombre": "CHIVITO DE TERNERA",
                "desc": "Mayonesa, tomate, cebolla, lechuga, ternera de primera, queso y bacon",
                "precio": 7.00,
                "cat": "BOCADILLOS Y CHIVITOS",
            },
            {
                "nombre": "CHIVITO DE CARNE DE CABALLO",
                "desc": "Mayonesa, tomate, cebolla, lechuga, sabrosa carne de caballo, queso y bacon",
                "precio": 8.00,
                "cat": "BOCADILLOS Y CHIVITOS",
            },
            {
                "nombre": "LOMO, QUESO Y BACON",
                "desc": "Lomo fresco a la plancha, queso fundido y bacon crujiente",
                "precio": 6.50,
                "cat": "BOCADILLOS Y CHIVITOS",
            },
            {
                "nombre": "BOCADILLO DE HAMBURGUESA COMPLETA",
                "desc": "Hamburguesa casera con lechuga, tomate, queso, cebolla y huevo frito",
                "precio": 5.50,
                "cat": "BOCADILLOS Y CHIVITOS",
            },
            {
                "nombre": "BOCADILLO AL GUSTO",
                "desc": "Elabora tu propio bocadillo con 3 ingredientes básicos",
                "precio": 5.50,
                "cat": "BOCADILLOS Y CHIVITOS",
            },
            # BRASCADAS
            {
                "nombre": "BRASCADA DE TERNERA",
                "desc": "Mayonesa, tomate, cebolla a la plancha, ternera tierna y jamón serrano",
                "precio": 6.50,
                "cat": "BRASCADAS",
            },
            {
                "nombre": "BRASCADA DE LOMO",
                "desc": "Mayonesa, tomate, cebolla a la plancha, lomo fresco y jamón serrano",
                "precio": 5.50,
                "cat": "BRASCADAS",
            },
            {
                "nombre": "BRASCADA DE CABALLO",
                "desc": "Mayonesa, tomate, cebolla a la plancha, carne de caballo y jamón serrano",
                "precio": 7.00,
                "cat": "BRASCADAS",
            },
            # ESPECIALES DE LA CASA
            {
                "nombre": "BOCADILLO CABRAMELIZADO LA GRANJA",
                "desc": "Cebolla caramelizada, queso de cabra, pechuga de pollo, queso edam, bacon y jamón serrano",
                "precio": 7.50,
                "cat": "ESPECIALES DE LA CASA",
            },
            {
                "nombre": "ESPECIAL SOBRASADA",
                "desc": "Sobrasada ibérica fundida con queso de cabra y miel",
                "precio": 6.00,
                "cat": "ESPECIALES DE LA CASA",
            },
            {
                "nombre": "LOMO, PIMIENTOS Y CEBOLLA",
                "desc": "Lomo fresco a la plancha con pimientos asados y cebolla confitada",
                "precio": 5.00,
                "cat": "ESPECIALES DE LA CASA",
            },
            {
                "nombre": "ESPECIAL BLANCO Y NEGRO",
                "desc": "Longaniza y morcilla a la brasa con habas tiernas",
                "precio": 5.50,
                "cat": "ESPECIALES DE LA CASA",
            },
            # DEL MAR
            {
                "nombre": "BOCADILLO DE SEPIA A LA PLANCHA",
                "desc": "Sepia fresca a la plancha con un toque de ajo y mayonesa",
                "precio": 8.00,
                "cat": "DEL MAR",
            },
            {
                "nombre": "CALAMARES A LA ANDALUZA",
                "desc": "Calamares rebozados crujientes con alioli casero",
                "precio": 8.00,
                "cat": "DEL MAR",
            },
            {
                "nombre": "REVUELTO DE GAMBAS",
                "desc": "Revuelto jugoso de gambas con ajos tiernos",
                "precio": 8.00,
                "cat": "DEL MAR",
            },
            {
                "nombre": "ANCHOAS Y QUESO",
                "desc": "Tomate rallado, anchoas del cantábrico y queso fresco",
                "precio": 6.00,
                "cat": "DEL MAR",
            },
            # BOCADILLOS CLÁSICOS
            {
                "nombre": "BOCADILLO VEGETAL",
                "desc": "Mayonesa, tomate, cebolla, lechuga, atún, huevo duro, maíz y espárragos",
                "precio": 5.50,
                "cat": "BOCADILLOS CLÁSICOS",
            },
            {
                "nombre": "TORTILLA DE PATATAS",
                "desc": "Jugosa tortilla de patatas casera con alioli",
                "precio": 5.50,
                "cat": "BOCADILLOS CLÁSICOS",
            },
            {
                "nombre": "TORTILLA FRANCESA COMPLETA",
                "desc": "Tortilla francesa con tomate rallado y longanizas de pascua",
                "precio": 5.00,
                "cat": "BOCADILLOS CLÁSICOS",
            },
            {
                "nombre": "EMBUTIDOS CON PISTO",
                "desc": "Selección de embutidos a la brasa con pisto casero",
                "precio": 5.50,
                "cat": "BOCADILLOS CLÁSICOS",
            },
            {
                "nombre": "PECHUGA EMPANADA",
                "desc": "Pechuga de pollo empanada crujiente con mayonesa, queso, bacon y patatas",
                "precio": 5.50,
                "cat": "BOCADILLOS CLÁSICOS",
            },
            {
                "nombre": "HUEVOS ROTOS CON CHISTORRA",
                "desc": "Huevos fritos con chistorra a la brasa, patatas panadera y alioli",
                "precio": 6.00,
                "cat": "BOCADILLOS CLÁSICOS",
            },
        ]

        for pdata in productos_data:
            cat_id = cat_objs[pdata["cat"]].id
            # Buscamos si existe por nombre exacto
            prod = db.query(Producto).filter(Producto.nombre == pdata["nombre"]).first()
            if not prod:
                prod = Producto(
                    nombre=pdata["nombre"],
                    descripcion=pdata["desc"],
                    precio=pdata["precio"],
                    categoria_id=cat_id,
                    stock_actual=50,  # Ponemos 50 de stock base
                    is_active=True,
                )
                db.add(prod)
            else:
                # Actualizar precios y descripciones si ya existen
                prod.descripcion = pdata["desc"]
                prod.precio = pdata["precio"]
                prod.categoria_id = cat_id
                prod.is_active = True

        db.commit()
        print("Menu nocturno (segun imagen) inyectado con exito.")
    except Exception as e:
        print(f"Error al inyectar menu nocturno: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_night_menu_image()
