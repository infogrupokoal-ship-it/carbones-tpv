import logging
from sqlalchemy import inspect, text
from backend.database import engine, Base
from backend.models import * # Import all models to ensure they are registered

logger = logging.getLogger("TPV_ENTERPRISE")

def migrate_schema():
    """
    Función de migración industrial: Detecta columnas faltantes y las añade automáticamente.
    Diseñado para evitar fallos de 'no such column' sin necesidad de Alembic en entornos ligeros.
    """
    logger.info("INICIANDO AUDITORÍA DE ESQUEMA DE BASE DE DATOS...")
    
    try:
        inspector = inspect(engine)
        
        # 1. Crear tablas si no existen
        Base.metadata.create_all(bind=engine)
        
        # 2. Verificar columnas faltantes en cada tabla
        for table_name, table_obj in Base.metadata.tables.items():
            existing_columns = [col['name'] for col in inspector.get_columns(table_name)]
            
            for column_name, column_obj in table_obj.columns.items():
                if column_name not in existing_columns:
                    logger.warning(f"COLUMNA FALTANTE DETECTADA: {table_name}.{column_name}. Migrando...")
                    
                    # Generar el tipo de dato para SQL
                    str(column_obj.type).split('(')[0] # Simplificado para SQLite/PG
                    
                    # Caso especial para SQLite (ALTER TABLE es limitado)
                    try:
                        with engine.connect() as conn:
                            # Construir comando ALTER TABLE
                            # Nota: SQLAlchemy no tiene un 'to_sql' fácil para columnas individuales
                            # Usamos una aproximación segura
                            alter_query = f'ALTER TABLE {table_name} ADD COLUMN {column_name} {column_obj.type.compile(engine.dialect)}'
                            conn.execute(text(alter_query))
                            conn.commit()
                        logger.info(f"ÉXITO: Columna {column_name} añadida a {table_name}.")
                    except Exception as e:
                        logger.error(f"FALLO AL MIGRAR {table_name}.{column_name}: {e}")
        
        logger.info("AUDITORÍA DE ESQUEMA COMPLETADA.")
        
    except Exception as e:
        logger.critical(f"ERROR FATAL DURANTE LA MIGRACIÓN: {e}")
        raise e

if __name__ == "__main__":
    # Configuración básica de log para ejecución directa
    logging.basicConfig(level=logging.INFO)
    migrate_schema()
