import sqlite3
import datetime
import requests
import os
import json

DB_PATH = "tpv_data.sqlite"
# WAHA URL, en el futuro se cambiara a la IP de la máquina WAHA si está en VPS
WAHA_URL = os.environ.get("WAHA_URL", "http://127.0.0.1:3000/api/sendText")
TELEFONO_ADMIN = "34604864187" # El tuyo personal

def generar_reporte_z():
    hoy = datetime.datetime.now()
    fecha_hoy_str = hoy.strftime("%Y-%m-%d")
    fecha_hoy_display = hoy.strftime("%d/%m/%Y")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Obtener pedidos pagados hoy
    # fecha stored as datetime, we use LIKE for string matching or datetime func in sqlite
    # Since datetime is stored as string 'YYYY-MM-DD HH:MM:SS.mmmmmm'
    query = """
        SELECT total, metodo_pago 
        FROM pedidos 
        WHERE estado != 'ESPERANDO_PAGO' 
        AND date(fecha) = ?
    """
    cursor.execute(query, (fecha_hoy_str,))
    pedidos = cursor.fetchall()
    
    total_efectivo = 0.0
    total_tarjeta = 0.0
    
    for row in pedidos:
        total = row[0]
        metodo = row[1]
        if metodo == "EFECTIVO":
            total_efectivo += total
        else:
            total_tarjeta += total
            
    total_caja = total_efectivo + total_tarjeta
    
    # Contar pollos asados vendidos
    # Asumimos que los pollos (id 1, o buscamos por nombre)
    # Busquemos el ID del pollo asado base
    cursor.execute("SELECT id FROM productos WHERE nombre LIKE '%Pollo Asado%' AND stock_base_id IS NULL LIMIT 1")
    pollo_res = cursor.fetchone()
    pollos_vendidos = 0
    if pollo_res:
        pollo_id = pollo_res[0]
        # Sumar movimientos de stock tipo VENTA para este pollo de hoy
        cursor.execute("""
            SELECT SUM(cantidad) 
            FROM movimientos_stock 
            WHERE producto_id = ? 
            AND tipo = 'VENTA' 
            AND date(fecha) = ?
        """, (pollo_id, fecha_hoy_str))
        res_movs = cursor.fetchone()
        if res_movs and res_movs[0]:
            pollos_vendidos = abs(res_movs[0])
            
    conn.close()
    
    mensaje = f"🐔 *CIERRE Z - CARBONES Y POLLOS* 🐔\n"
    mensaje += f"📅 Fecha: {fecha_hoy_display}\n\n"
    mensaje += f"💰 Efectivo: {total_efectivo:.2f} €\n"
    mensaje += f"💳 Tarjeta: {total_tarjeta:.2f} €\n"
    mensaje += f"------------------------\n"
    mensaje += f"📊 *TOTAL CAJA: {total_caja:.2f} €*\n\n"
    mensaje += f"🍗 Pollos Vendidos: {int(pollos_vendidos)}\n"
    
    return mensaje

def enviar_whatsapp(mensaje):
    payload = {
        "chatId": f"{TELEFONO_ADMIN}@c.us",
        "text": mensaje,
        "session": "default"
    }
    headers = {"Content-Type": "application/json"}
    
    print(f"Enviando WhatsApp a {TELEFONO_ADMIN}...")
    try:
        response = requests.post(WAHA_URL, json=payload, headers=headers, timeout=10)
        if response.status_code == 201 or response.status_code == 200:
            print("WhatsApp enviado correctamente.")
        else:
            print(f"Error enviando WhatsApp: {response.text}")
    except Exception as e:
        print(f"No se pudo contactar con WAHA: {e}")

if __name__ == "__main__":
    msg = generar_reporte_z()
    print("-------------------------")
    print(msg)
    print("-------------------------")
    enviar_whatsapp(msg)
