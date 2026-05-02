import sqlite3
import json

def get_categories():
    try:
        conn = sqlite3.connect('tpv_data.sqlite')
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre FROM categorias")
        cats = [{"id": row[0], "nombre": row[1]} for row in cursor.fetchall()]
        conn.close()
        print(json.dumps(cats))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_categories()
