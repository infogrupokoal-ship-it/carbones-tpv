import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Categoria, Producto, Usuario, Review, Proveedor, Ingrediente, Receta, Fichaje
from datetime import datetime, timedelta

DB_PATH = "sqlite:///tpv_data.sqlite"

def reset_db():
    print("Iniciando Hard Reset de la Base de Datos...")
    engine = create_engine(DB_PATH, connect_args={"check_same_thread": False})
    
    # Dropping all tables to ensure a clean slate
    Base.metadata.drop_all(bind=engine)
    print("Tablas antiguas eliminadas.")
    
    # Creating tables with new schema
    Base.metadata.create_all(bind=engine)
    print("Nuevas tablas creadas.")
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("Insertando Usuarios...")
        u1 = Usuario(username="encargado_mañana", password="123", rol="MANANA")
        u2 = Usuario(username="encargado_tarde", password="123", rol="TARDE")
        u3 = Usuario(username="admin", password="123", rol="ADMIN")
        u4 = Usuario(username="cocina", password="123", rol="COCINA")
        db.add_all([u1, u2, u3, u4])
        db.flush()
        
        # Fichajes (HR)
        db.add_all([
            Fichaje(usuario_id=u1.id, tipo="ENTRADA", fecha=datetime.now() - timedelta(hours=4)),
            Fichaje(usuario_id=u4.id, tipo="ENTRADA", fecha=datetime.now() - timedelta(hours=4)),
            Fichaje(usuario_id=u4.id, tipo="INICIO_PAUSA", fecha=datetime.now() - timedelta(minutes=30)),
        ])
        
        print("Insertando Proveedores...")
        prov_pollos = Proveedor(nombre="Granjas Del Sur", telefono="600111222", email="ventas@granjassur.es", dias_entrega="Lunes, Jueves")
        prov_carbon = Proveedor(nombre="Carbones Ecológicos S.A.", telefono="600333444", email="info@carbones.es", dias_entrega="Martes")
        prov_bebidas = Proveedor(nombre="Distribuciones Bebidas", telefono="600555666", email="pedidos@distribuciones.es", dias_entrega="Miércoles, Viernes")
        db.add_all([prov_pollos, prov_carbon, prov_bebidas])
        db.flush()
        
        print("Insertando Ingredientes (Materia Prima)...")
        ing_pollo = Ingrediente(nombre="Pollo Crudo Entero", unidad_medida="UD", stock_actual=250, stock_minimo=50, coste_unitario=2.50, proveedor_id=prov_pollos.id)
        ing_carbon = Ingrediente(nombre="Carbón Vegetal", unidad_medida="KG", stock_actual=200, stock_minimo=50, coste_unitario=1.20, proveedor_id=prov_carbon.id)
        ing_patata = Ingrediente(nombre="Patata Cruda", unidad_medida="KG", stock_actual=100, stock_minimo=20, coste_unitario=0.80, proveedor_id=prov_pollos.id) # Simulando mismo proveedor
        ing_bandeja = Ingrediente(nombre="Bandeja Aluminio Asado", unidad_medida="UD", stock_actual=500, stock_minimo=100, coste_unitario=0.10, proveedor_id=prov_carbon.id)
        db.add_all([ing_pollo, ing_carbon, ing_patata, ing_bandeja])
        db.flush()

        print("Insertando Categorías...")
        cat_pollos = Categoria(nombre="Pollos Asados", orden=1)
        cat_pizzas = Categoria(nombre="Pizzas Artesanas", orden=2)
        cat_guarniciones = Categoria(nombre="Guarniciones", orden=3)
        cat_bebidas = Categoria(nombre="Bebidas", orden=4)
        cat_salsas = Categoria(nombre="Salsas y Extras", orden=7)
        db.add_all([cat_pollos, cat_pizzas, cat_guarniciones, cat_bebidas, cat_salsas])
        db.flush()
        
        print("Insertando Productos Finales...")
        p_entero = Producto(nombre="Pollo Entero", precio=12.00, categoria_id=cat_pollos.id, url_imagen="/static/img/pollo_entero.jpg", descripcion="Jugoso.")
        p_medio = Producto(nombre="Medio Pollo", precio=6.50, categoria_id=cat_pollos.id, url_imagen="/static/img/medio_pollo.jpg")
        p_cuarto = Producto(nombre="Cuarto de Pollo", precio=3.50, categoria_id=cat_pollos.id, url_imagen="/static/img/cuarto_pollo.jpg")
        
        prod_patatas = Producto(nombre="Patatas Fritas Grandes", precio=4.00, categoria_id=cat_guarniciones.id)
        prod_refresco = Producto(nombre="Refresco Cola", precio=1.80, categoria_id=cat_bebidas.id)
        
        db.add_all([p_entero, p_medio, p_cuarto, prod_patatas, prod_refresco])
        db.flush()
        
        print("Insertando Recetas (Escandallos)...")
        # 1 Pollo Entero = 1 Pollo Crudo + 0.5kg Carbón + 1 Bandeja Aluminio
        db.add_all([
            Receta(producto_id=p_entero.id, ingrediente_id=ing_pollo.id, cantidad_necesaria=1.0),
            Receta(producto_id=p_entero.id, ingrediente_id=ing_carbon.id, cantidad_necesaria=0.5),
            Receta(producto_id=p_entero.id, ingrediente_id=ing_bandeja.id, cantidad_necesaria=1.0),
            
            # Medio Pollo = 0.5 Pollo Crudo + 0.25kg Carbón + 1 Bandeja (siempre consume 1 bandeja)
            Receta(producto_id=p_medio.id, ingrediente_id=ing_pollo.id, cantidad_necesaria=0.5),
            Receta(producto_id=p_medio.id, ingrediente_id=ing_carbon.id, cantidad_necesaria=0.25),
            Receta(producto_id=p_medio.id, ingrediente_id=ing_bandeja.id, cantidad_necesaria=1.0),
            
            # Patatas Grandes = 0.8kg Patata Cruda
            Receta(producto_id=prod_patatas.id, ingrediente_id=ing_patata.id, cantidad_necesaria=0.8),
        ])
        
        print("Insertando Reviews de Ejemplo para Dashboard...")
        rev1 = Review(rating=5, comentario="¡Los pollos asados están espectaculares! El servicio muy rápido.", analisis_ia="Sentimiento positivo, destaca calidad y velocidad.")
        db.add(rev1)
        
        db.commit()
        print("¡Hard Reset y Seed Completados con Éxito!")
        
    except Exception as e:
        db.rollback()
        print("Error durante el seed:", e)
    finally:
        db.close()

if __name__ == "__main__":
    reset_db()
