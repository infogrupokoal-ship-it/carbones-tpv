import sqlite3

def check_products():
    conn = sqlite3.connect('tpv_data.sqlite')
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, categoria, imagen_url FROM productos")
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    conn.close()

if __name__ == "__main__":
    check_products()
