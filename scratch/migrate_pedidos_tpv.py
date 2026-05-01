import sqlite3
import os

def migrate():
    db_path = 'tpv_data.sqlite'
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        print("Adding columns to 'pedidos' table in tpv_data.sqlite...")
        cursor.execute("ALTER TABLE pedidos ADD COLUMN metodo_envio VARCHAR(20) DEFAULT 'LOCAL'")
        cursor.execute("ALTER TABLE pedidos ADD COLUMN direccion TEXT")
        conn.commit()
        print("Migration successful!")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("Columns already exist. Skipping.")
        else:
            print(f"Operational error: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
