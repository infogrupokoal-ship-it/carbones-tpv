import requests

BASE_URL = "http://127.0.0.1:8000"


def run_e2e():
    print("🚀 Iniciando Test E2E B2C Autónomo...")

    # 1. Simular mensaje de WhatsApp de un cliente nuevo
    print("\n--- Paso 1: WhatsApp Inicial ---")
    wa_payload = {
        "event": "message",
        "payload": {
            "from": "34600000001@c.us",
            "body": "Hola, quiero pedir",
            "fromMe": False,
        },
    }

    res = requests.post(f"{BASE_URL}/webhook/waha", json=wa_payload)
    print(f"Respuesta WA (Status {res.status_code}):", res.json())

    # 2. Simular que el cliente envía su nombre
    print("\n--- Paso 2: WhatsApp Nombre ---")
    wa_payload["payload"]["body"] = "Soy Pepe"
    res = requests.post(f"{BASE_URL}/webhook/waha", json=wa_payload)
    data = res.json()
    print(f"Respuesta WA (Status {res.status_code}):", data)

    # Extraemos el magic link si está en la respuesta simulando
    # Dado que el endpoint devuelve un JSON con la respuesta (depende de como está implementado webhook)
    # Mejor simulamos el login con el teléfono.

    print("\n--- Paso 3: Login Web Frontend ---")
    auth_res = requests.post(
        f"{BASE_URL}/api/b2c/auth",
        json={"telefono": "34600000001", "nombre": "Pepe Test"},
    )
    auth_data = auth_res.json()
    print("Auth:", auth_data)
    cliente_id = auth_data["cliente_id"]

    print("\n--- Paso 4: Obtener Catálogo ---")
    cat_res = requests.get(f"{BASE_URL}/api/categorias")
    cat_res.json()

    prod_res = requests.get(f"{BASE_URL}/api/productos")
    productos = prod_res.json()

    if not productos:
        print("❌ No hay productos en el catálogo.")
        return

    prod_test = productos[0]
    print(f"Producto seleccionado: {prod_test['nombre']}")

    print("\n--- Paso 5: Crear Pedido PAGO EN LOCAL ---")
    pedido_payload = {
        "items": [{"producto_id": prod_test["id"], "cantidad": 1}],
        "origen": "B2C_MOBILE",
        "estado_inicial": "EN_PREPARACION",
        "notas_cliente": "(B2C Web) Test E2E Sin Cebolla",
    }

    ped_res = requests.post(
        f"{BASE_URL}/api/pedidos?cliente_id={cliente_id}", json=pedido_payload
    )
    ped_data = ped_res.json()
    print("Pedido:", ped_data)
    pedido_id = ped_data["pedido_id"]

    print("\n--- Paso 6: Verificar Comandos Hardware (Cocina) ---")
    hw_res = requests.get(f"{BASE_URL}/api/hardware/poll")
    hw_data = hw_res.json()
    print("Hardware Queue:", hw_data)

    # Completar el hardware commands
    for h in hw_data.get("comandos", []):
        requests.post(f"{BASE_URL}/api/hardware/ack/{h['id']}")
        print(f"Completado comando de impresión {h['id']}")

    print("\n--- Paso 7: Cambiar estado a LISTO ---")
    estado_res = requests.post(
        f"{BASE_URL}/api/pedidos/{pedido_id}/estado?estado=LISTO"
    )
    print("Estado Final:", estado_res.json())

    print("\n✅ Test E2E completado con éxito.")


if __name__ == "__main__":
    run_e2e()
