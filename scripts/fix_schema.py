import os
import sys
from sqlalchemy import create_engine, text

# Asegurar que estamos en el directorio correcto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATABASE_URL = "sqlite:///./tpv_data.sqlite"
engine = create_engine(DATABASE_URL)

def add_column(table, column, definition):
    with engine.begin() as conn:
        try:
            conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {definition}"))
            print(f"Columna '{column}' añadida a '{table}'.")
        except Exception as e:
            # Si ya existe, ignorar
            pass

if __name__ == "__main__":
    print("Iniciando parche de esquema...")
    # Productos
    add_column("productos", "stock_actual", "FLOAT DEFAULT 0.0")
    add_column("productos", "stock_minimo", "FLOAT DEFAULT 0.0")
    add_column("productos", "stock_base_id", "INTEGER")
    add_column("productos", "factor_stock", "FLOAT DEFAULT 1.0")
    add_column("productos", "imagen_url", "VARCHAR")
    add_column("productos", "alergenos", "VARCHAR")
    add_column("productos", "info_nutricional", "VARCHAR")
    
    # Pedidos
    add_column("pedidos", "descuento_aplicado", "FLOAT DEFAULT 0.0")
    add_column("pedidos", "base_imponible_10", "FLOAT DEFAULT 0.0")
    add_column("pedidos", "cuota_iva_10", "FLOAT DEFAULT 0.0")
    add_column("pedidos", "base_imponible_21", "FLOAT DEFAULT 0.0")
    add_column("pedidos", "cuota_iva_21", "FLOAT DEFAULT 0.0")
    add_column("pedidos", "origen", "VARCHAR DEFAULT 'POS'")
    add_column("pedidos", "notas_cliente", "VARCHAR")
    add_column("pedidos", "cubiertos_qty", "INTEGER DEFAULT 0")

    print("Esquema parcheado exitosamente.")
