import sqlite3

def check_schema():
    conn = sqlite3.connect('tpv_data.sqlite')
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(productos)")
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    conn.close()

if __name__ == "__main__":
    check_schema()
