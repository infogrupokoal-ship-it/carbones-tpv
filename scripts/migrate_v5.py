import sys
import os

# Añadir path del proyecto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import engine, Base

def run_migration():
    print("🚀 INICIANDO MIGRACIÓN ESTRUCTURAL V5.1...")
    try:
        # 1. Crear tablas si no existen
        Base.metadata.create_all(bind=engine)
        
        # 2. Inyección manual de columnas (SQLite no soporta ADD COLUMN condicional nativo en una sola sentencia simple para todas)
        with engine.connect() as conn:
            try:
                conn.execute("ALTER TABLE productos ADD COLUMN alergenos VARCHAR")
                print("➕ Columna 'alergenos' añadida.")
            except:
                print("ℹ️ Columna 'alergenos' ya existe.")
                
            try:
                conn.execute("ALTER TABLE productos ADD COLUMN info_nutricional TEXT")
                print("➕ Columna 'info_nutricional' añadida.")
            except:
                print("ℹ️ Columna 'info_nutricional' ya existe.")
                
        print("✅ Esquemas de base de datos verificados/actualizados.")
    except Exception as e:
        print(f"❌ Error verificando esquemas: {e}")

if __name__ == "__main__":
    run_migration()
