from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.models import Categoria, Producto

DB_PATH = "sqlite:///tpv_data.sqlite"
engine = create_engine(DB_PATH, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def seed_day_menu():
    db = SessionLocal()
    try:
        # Categorías del Turno Día (Orden < 10)
        categorias_data = [
            {"nombre": "Pollos Asados", "orden": 1},
            {"nombre": "Arroces y Paellas", "orden": 2},
            {"nombre": "Carnes y Guisos", "orden": 3},
            {"nombre": "Guarniciones", "orden": 4},
            {"nombre": "Bebidas", "orden": 5},
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

        productos_data = [
            # Arroces (Raciones a 5€)
            {
                "nombre": "Ración de Paella Valenciana",
                "desc": "Auténtica paella valenciana con pollo, conejo y garrofón",
                "precio": 5.00,
                "cat": "Arroces y Paellas",
            },
            {
                "nombre": "Ración de Arroz al Horno",
                "desc": "Arroz al horno tradicional con costilla, morcilla y garbanzos",
                "precio": 5.00,
                "cat": "Arroces y Paellas",
            },
            {
                "nombre": "Ración de Arroz a Banda",
                "desc": "Arroz a banda marinero con su alioli casero",
                "precio": 5.00,
                "cat": "Arroces y Paellas",
            },
            {
                "nombre": "Ración de Arroz Negro",
                "desc": "Arroz negro con calamares y fina tinta de sepia",
                "precio": 5.00,
                "cat": "Arroces y Paellas",
            },
            {
                "nombre": "Ración de Fideuá de Mariscos",
                "desc": "Fideuá tradicional con marisco fresco",
                "precio": 5.00,
                "cat": "Arroces y Paellas",
            },
            # Pollos
            {
                "nombre": "Pollo Entero Asado al Carbón",
                "desc": "Pollo asado a leña con nuestro adobo secreto, jugoso y crujiente",
                "precio": 12.00,
                "cat": "Pollos Asados",
            },
            {
                "nombre": "Medio Pollo Asado",
                "desc": "Mitad de pollo asado al carbón",
                "precio": 6.50,
                "cat": "Pollos Asados",
            },
            {
                "nombre": "Cuarto de Pollo Asado",
                "desc": "Cuarto de pollo (pechuga o muslo)",
                "precio": 3.50,
                "cat": "Pollos Asados",
            },
            {
                "nombre": "Alitas de Pollo a la Brasa",
                "desc": "Ración de alitas de pollo asadas con salsa barbacoa suave (8 uds)",
                "precio": 6.00,
                "cat": "Pollos Asados",
            },
            # Carnes y Guisos (Hasta 12€)
            {
                "nombre": "Quijadas de Cerdo en Salsa",
                "desc": "Carrilleras de cerdo guisadas a fuego lento con reducción de vino tinto",
                "precio": 11.50,
                "cat": "Carnes y Guisos",
            },
            {
                "nombre": "Codillo Asado al Horno",
                "desc": "Codillo estilo rústico asado lentamente en su jugo",
                "precio": 12.00,
                "cat": "Carnes y Guisos",
            },
            {
                "nombre": "Ragout de Ternera",
                "desc": "Estofado tradicional de ternera con verduras de la huerta",
                "precio": 10.50,
                "cat": "Carnes y Guisos",
            },
            {
                "nombre": "Costillar de Cerdo a la BBQ",
                "desc": "Costillar de cerdo asado a baja temperatura con salsa barbacoa",
                "precio": 12.00,
                "cat": "Carnes y Guisos",
            },
            {
                "nombre": "Albóndigas Caseras en Salsa",
                "desc": "Albóndigas de ternera y cerdo en rica salsa de tomate casera",
                "precio": 8.50,
                "cat": "Carnes y Guisos",
            },
            # Guarniciones
            {
                "nombre": "Patatas Asadas",
                "desc": "Patatas asadas al carbón con un toque de hierbas provenzales",
                "precio": 4.00,
                "cat": "Guarniciones",
            },
            {
                "nombre": "Patatas Fritas Caseras",
                "desc": "Ración de patatas fritas cortadas a mano",
                "precio": 3.50,
                "cat": "Guarniciones",
            },
            {
                "nombre": "Ración de Croquetas Caseras",
                "desc": "Croquetas caseras de jamón ibérico o pollo asado (6 uds)",
                "precio": 5.50,
                "cat": "Guarniciones",
            },
            {
                "nombre": "Ensaladilla Rusa Tradicional",
                "desc": "Ración de ensaladilla casera con atún y mayonesa suave",
                "precio": 5.00,
                "cat": "Guarniciones",
            },
            {
                "nombre": "Pimientos de Padrón",
                "desc": "Ración de pimientos de Padrón fritos",
                "precio": 4.50,
                "cat": "Guarniciones",
            },
            # Bebidas
            {
                "nombre": "Refresco Cola 33cl",
                "desc": "",
                "precio": 1.80,
                "cat": "Bebidas",
            },
            {
                "nombre": "Refresco Naranja/Limón 33cl",
                "desc": "",
                "precio": 1.80,
                "cat": "Bebidas",
            },
            {
                "nombre": "Lata de Cerveza 33cl",
                "desc": "Cerveza rubia tradicional",
                "precio": 2.00,
                "cat": "Bebidas",
            },
            {
                "nombre": "Cerveza Artesana",
                "desc": "Cerveza artesana local",
                "precio": 3.50,
                "cat": "Bebidas",
            },
            {
                "nombre": "Agua Mineral 50cl",
                "desc": "",
                "precio": 1.50,
                "cat": "Bebidas",
            },
            {
                "nombre": "Vino Tinto (Botella)",
                "desc": "Botella de vino tinto de la casa (Rioja/Ribera)",
                "precio": 9.00,
                "cat": "Bebidas",
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

        # Desactivar categorías de día antiguas que no esten en la nueva lista para limpiar la vista.
        # En realidad podemos simplemente dejar que el sistema las ordene.

        db.commit()
        print("Menu de dia inyectado con exito.")
    except Exception as e:
        print(f"Error al inyectar menu de dia: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_day_menu()
