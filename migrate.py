import sqlite3
import sys

conn = sqlite3.connect('tpv_data.sqlite')
c = conn.cursor()

commands = [
    "ALTER TABLE productos ADD COLUMN impuesto FLOAT DEFAULT 10.0;",
    "ALTER TABLE categorias ADD COLUMN is_synced BOOLEAN DEFAULT 0;",
    "ALTER TABLE pedidos ADD COLUMN cubiertos_qty INTEGER DEFAULT 0;",
    "ALTER TABLE item_pedido ADD COLUMN is_synced BOOLEAN DEFAULT 0;",
    "ALTER TABLE item_pedido ADD COLUMN remote_id INTEGER;",
    "ALTER TABLE pedidos ADD COLUMN base_imponible_10 FLOAT DEFAULT 0.0;",
    "ALTER TABLE pedidos ADD COLUMN cuota_iva_10 FLOAT DEFAULT 0.0;",
    "ALTER TABLE pedidos ADD COLUMN base_imponible_21 FLOAT DEFAULT 0.0;",
    "ALTER TABLE pedidos ADD COLUMN cuota_iva_21 FLOAT DEFAULT 0.0;",
    "ALTER TABLE pedidos ADD COLUMN is_synced BOOLEAN DEFAULT 0;",
    "ALTER TABLE pedidos ADD COLUMN remote_id INTEGER;",
    "ALTER TABLE pedidos ADD COLUMN tipo_entrega VARCHAR DEFAULT 'LOCAL';",
    "ALTER TABLE pedidos ADD COLUMN latitud_actual FLOAT;",
    "ALTER TABLE pedidos ADD COLUMN longitud_actual FLOAT;",
    "ALTER TABLE pedidos ADD COLUMN distancia_metros FLOAT;",
    "ALTER TABLE clientes ADD COLUMN is_synced BOOLEAN DEFAULT 0;",
    "ALTER TABLE clientes ADD COLUMN remote_id INTEGER;",
    "ALTER TABLE productos ADD COLUMN is_synced BOOLEAN DEFAULT 0;",
    "ALTER TABLE productos ADD COLUMN remote_id INTEGER;",
    "ALTER TABLE categorias ADD COLUMN remote_id INTEGER;",
    "ALTER TABLE movimientos_stock ADD COLUMN is_synced BOOLEAN DEFAULT 0;",
    "ALTER TABLE movimientos_stock ADD COLUMN remote_id INTEGER;"
]

for cmd in commands:
    try:
        c.execute(cmd)
    except Exception as e:
        pass # Ignorar si la columna ya existe

conn.commit()
conn.close()
print("Migraciones Python OK")
