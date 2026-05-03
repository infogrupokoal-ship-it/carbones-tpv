import sqlite3
from datetime import datetime

conn = sqlite3.connect('tpv_data.sqlite')
c = conn.cursor()

today = datetime.now().isoformat()

# Try to insert some fake data for testing the audit endpoint.
try:
    # Insert a few completed orders
    c.execute("INSERT INTO pedidos (id, total, estado, metodo_pago, fecha) VALUES (?, ?, ?, ?, ?)", (90001, 24.50, 'completado', 'tarjeta', today))
    c.execute("INSERT INTO pedidos (id, total, estado, metodo_pago, fecha) VALUES (?, ?, ?, ?, ?)", (90002, 12.00, 'completado', 'efectivo', today))
    c.execute("INSERT INTO pedidos (id, total, estado, metodo_pago, fecha) VALUES (?, ?, ?, ?, ?)", (90003, 45.90, 'completado', 'tarjeta', today))

    # Insert some canceled orders (Anomalies)
    c.execute("INSERT INTO pedidos (id, total, estado, metodo_pago, fecha) VALUES (?, ?, ?, ?, ?)", (90004, 150.00, 'cancelado', 'efectivo', today))
    c.execute("INSERT INTO pedidos (id, total, estado, metodo_pago, fecha) VALUES (?, ?, ?, ?, ?)", (90005, 80.00, 'cancelado', 'tarjeta', today))

    # Insert some logs
    c.execute("INSERT INTO logs_operativos (id, modulo, nivel, mensaje, fecha) VALUES (?, ?, ?, ?, ?)", (80001, 'Caja', 'WARNING', 'Descuadre de 5 euros en turno mañana', today))
    c.execute("INSERT INTO logs_operativos (id, modulo, nivel, mensaje, fecha) VALUES (?, ?, ?, ?, ?)", (80002, 'Seguridad', 'CRITICAL', 'Múltiples intentos de anulación de tickets sin permiso', today))
    
    conn.commit()
    print("Test data seeded successfully!")
except sqlite3.IntegrityError:
    print("Test data already exists.")

conn.close()
