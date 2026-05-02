import sqlite3
import os
import sys

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

db_path = r'd:\proyecto\carbones_y_pollos_tpv\tpv_data.sqlite'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, imagen_url FROM categorias;")
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    conn.close()
else:
    print(f"File not found: {db_path}")
