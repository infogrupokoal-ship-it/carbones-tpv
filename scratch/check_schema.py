import sqlite3

def check_schema():
    conn = sqlite3.connect('tpv_data.sqlite')
    cursor = conn.cursor()
    
    tables = ['pedidos', 'productos']
    for table in tables:
        print(f"--- Schema for {table} ---")
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        for col in columns:
            print(col)
    
    conn.close()

if __name__ == "__main__":
    check_schema()
