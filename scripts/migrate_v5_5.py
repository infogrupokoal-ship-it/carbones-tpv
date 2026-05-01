import sys
import os

# Añadir path del proyecto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import engine, Base
from sqlalchemy import text

def run_migration():
    print("INICIANDO MIGRACION ESTRUCTURAL V5.5 (Gobernanza y Auditoria)...")
    try:
        # 1. Crear nuevas tablas (AuditLog)
        Base.metadata.create_all(bind=engine)
        print("Nuevas tablas creadas (AuditLog).")
        
        # 2. Inyección manual de columnas para Soft Delete
        with engine.connect() as conn:
            # Añadir is_active a categorias
            try:
                conn.execute(text("ALTER TABLE categorias ADD COLUMN is_active BOOLEAN DEFAULT 1"))
                print("Columna 'is_active' añadida a 'categorias'.")
            except Exception as e:
                print(f"Columna 'is_active' ya existe en 'categorias': {e}")
                
            # Añadir impuesto a productos (fix)
            try:
                conn.execute(text("ALTER TABLE productos ADD COLUMN impuesto FLOAT DEFAULT 10.0"))
                print("Columna 'impuesto' añadida a 'productos'.")
            except Exception as e:
                print(f"Columna 'impuesto' ya existe en 'productos': {e}")

            # Añadir is_active a ingredientes
            try:
                conn.execute(text("ALTER TABLE ingredientes ADD COLUMN is_active BOOLEAN DEFAULT 1"))
                print("Columna 'is_active' añadida a 'ingredientes'.")
            except Exception as e:
                print(f"Columna 'is_active' ya existe en 'ingredientes': {e}")
                
            # Añadir is_active a proveedores
            try:
                conn.execute(text("ALTER TABLE proveedores ADD COLUMN is_active BOOLEAN DEFAULT 1"))
                print("Columna 'is_active' añadida a 'proveedores'.")
            except Exception as e:
                print(f"Columna 'is_active' ya existe en 'proveedores': {e}")
                
            conn.commit()
                
        print("Esquemas de base de datos V5.5 verificados/actualizados.")
    except Exception as e:
        print(f"Error verificando esquemas V5.5: {e}")

if __name__ == "__main__":
    run_migration()
