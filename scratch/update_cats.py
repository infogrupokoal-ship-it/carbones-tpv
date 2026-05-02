import sqlite3
import os

db_path = r'd:\proyecto\carbones_y_pollos_tpv\tpv_data.sqlite'
updates = [
    ('BOCADILLOS Y CHIVITOS', '/static/assets/minimalist/bocadillo.png'),
    ('BRASCADAS', '/static/assets/minimalist/pollo.png'),
    ('ESPECIALES DE LA CASA', '/static/assets/minimalist/pollo.png'),
    ('DEL MAR', '/static/assets/minimalist/arroz.png'),
    ('BOCADILLOS CLÁSICOS', '/static/assets/minimalist/bocadillo.png'),
    ('PIZZAS ARTESANAS', '/static/assets/minimalist/pizza.png')
]

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    for nombre, url in updates:
        cursor.execute("UPDATE categorias SET imagen_url = ? WHERE nombre = ? AND imagen_url IS NULL", (url, nombre))
    conn.commit()
    print(f"Updated {cursor.rowcount} rows.")
    conn.close()
else:
    print(f"File not found: {db_path}")
