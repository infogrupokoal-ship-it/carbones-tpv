import sqlite3

def check_schema():
    conn = sqlite3.connect('tpv_data.sqlite')
    cursor = conn.cursor()
    
    for table in ['pedidos', 'productos']:
        print(f"\n--- Schema for {table} ---")
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        for col in columns:
            print(col)
    
    conn.close()

if __name__ == "__main__":
    check_schema()
