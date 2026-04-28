import sqlite3
import datetime
import requests
import os

DB_PATH = "tpv_data.sqlite"
WAHA_URL = os.environ.get("WAHA_URL", "http://113.30.148.104:3000")
WAHA_SESSION = os.environ.get("WAHA_SESSION", "carbones")
WAHA_API_KEY = os.environ.get("WAHA_HTTP_API_KEY", "1060705b0a574d1fbc92fa10a2b5aca7")
TELEFONO_ADMIN = os.environ.get("TELEFONO_ADMIN", "34604864187")

def generar_reporte_z():
    hoy = datetime.datetime.now()
    fecha_hoy_str = hoy.strftime("%Y-%m-%d")
    fecha_hoy_display = hoy.strftime("%d/%m/%Y")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Obtener pedidos pagados hoy
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
    
    # Obtener IDs de categorías perecederas
    cursor.execute("SELECT id FROM categorias WHERE nombre IN ('Pollos Asados', 'Guarniciones')")
    cat_ids = [row[0] for row in cursor.fetchall()]
    
    # Obtener productos (para el conteo de mermas y pollos vendidos)
    cursor.execute("SELECT id, nombre, stock_actual, categoria_id, precio FROM productos WHERE stock_base_id IS NULL")
    productos = cursor.fetchall()
    
    sobrantes_texto = ""
    pollos_vendidos = 0
    mermas_vaciadas = 0
    coste_total_mermas = 0.0
    
    for p in productos:
        p_id, p_nombre, p_stock, p_cat_id, p_precio = p
        
        # Si es Pollo Asado, calcular vendidos hoy
        if "Pollo" in p_nombre:
            cursor.execute("""
                SELECT SUM(cantidad) 
                FROM movimientos_stock 
                WHERE producto_id = ? 
                AND tipo = 'VENTA' 
                AND date(fecha) = ?
            """, (p_id, fecha_hoy_str))
            res_movs = cursor.fetchone()
            if res_movs and res_movs[0]:
                pollos_vendidos += abs(res_movs[0])
                
        # MAGIA FASE 3: Si es producto perecedero y tiene stock positivo, se convierte en merma/sobrante automáticamente
        if p_cat_id in cat_ids and p_stock > 0:
            merma_qty = p_stock
            
            # Estimación de coste perdido (Asumimos que el coste es un 40% del precio de venta final)
            coste_estimado = merma_qty * (p_precio * 0.40)
            coste_total_mermas += coste_estimado
            
            sobrantes_texto += f"🗑 {p_nombre}: {merma_qty} uds. (-{coste_estimado:.2f}€)\n"
            
            # Registrar el movimiento de purga
            cursor.execute("""
                INSERT INTO movimientos_stock (producto_id, cantidad, tipo, descripcion, fecha)
                VALUES (?, ?, 'SOBRANTE_DIA_ANTERIOR', 'Vaciado automático fin de día', ?)
            """, (p_id, -merma_qty, hoy.strftime("%Y-%m-%d %H:%M:%S")))
            
            # Vaciar el stock
            cursor.execute("UPDATE productos SET stock_actual = 0 WHERE id = ?", (p_id,))
            mermas_vaciadas += 1
            
        elif p_stock != 0 and p_cat_id not in cat_ids:
            # Productos no perecederos con stock (Bebidas, etc), se listan pero no se vacían
            sobrantes_texto += f"📦 {p_nombre}: {p_stock}\n"

    conn.commit()

    conn.close()
    
    mensaje = f"🐔 *CIERRE Z - CARBONES Y POLLOS* 🐔\n"
    mensaje += f"📅 Fecha: {fecha_hoy_display}\n\n"
    mensaje += f"💰 Efectivo: {total_efectivo:.2f} €\n"
    mensaje += f"💳 Tarjeta: {total_tarjeta:.2f} €\n"
    mensaje += f"------------------------\n"
    mensaje += f"📊 *TOTAL CAJA: {total_caja:.2f} €*\n\n"
    mensaje += f"🍗 Pollos Vendidos Hoy: {int(pollos_vendidos)}\n\n"
    if coste_total_mermas > 0:
        mensaje += f"🚨 *COSTE MERMAS HOY: -{coste_total_mermas:.2f} €*\n\n"
    mensaje += f"📦 *INVENTARIO FINAL (SOBRANTES)*:\n"
    mensaje += sobrantes_texto if sobrantes_texto else "Sin sobrantes."
    
    # ---------------------------------------------
    # FASE 2/3 EXPANDIDA: AUDITORIA EN BASE DE DATOS
    # ---------------------------------------------
    try:
        cursor.execute("""
            INSERT INTO reportes_z (fecha_cierre, total_efectivo, total_tarjeta, total_caja, pollos_vendidos, coste_mermas, resumen_texto)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (hoy.strftime("%Y-%m-%d %H:%M:%S"), total_efectivo, total_tarjeta, total_caja, pollos_vendidos, coste_total_mermas, mensaje))
        conn.commit()
    except Exception as e:
        print(f"Nota: No se pudo guardar en reportes_z ({e}). Asegúrate de reiniciar el servidor para que cree la tabla.")

    conn.close()
    
    return mensaje

def enviar_whatsapp(mensaje):
    payload = {
        "chatId": f"{TELEFONO_ADMIN}@c.us",
        "text": mensaje,
        "session": WAHA_SESSION
    }
    headers = {"Content-Type": "application/json"}
    if WAHA_API_KEY:
        headers["X-Api-Key"] = WAHA_API_KEY
        
    print(f"Enviando WhatsApp a {TELEFONO_ADMIN}...")
    try:
        response = requests.post(f"{WAHA_URL}/api/sendText", json=payload, headers=headers, timeout=10)
        if response.status_code in [200, 201]:
            print("WhatsApp enviado correctamente.")
        else:
            print(f"Error enviando WhatsApp: {response.text}")
    except Exception as e:
        print(f"No se pudo contactar con WAHA: {e}")

if __name__ == "__main__":
    msg = generar_reporte_z()
    print(msg)
    enviar_whatsapp(msg)
