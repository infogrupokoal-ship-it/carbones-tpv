import os
import json
from datetime import datetime

try:
    import requests
except Exception:
    requests = None

PRINT_MODE = os.getenv("PRINT_MODE", "mock").lower()  # mock | bridge | escpos
LOCAL_PRINTER_URL = os.getenv("LOCAL_PRINTER_URL", "http://127.0.0.1:8181/print")


def _ticket_text(payload: dict) -> str:
    lines = []
    lines.append("CARBONES Y POLLOS LA GRANJA S.L.")
    lines.append("CIF: B-12345678")
    lines.append("C/ Ejemplo 123, Valencia")
    lines.append("Tel: 96 123 45 67")
    lines.append("-" * 32)
    lines.append(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    lines.append("-" * 32)
    lines.append(f"Pedido: {payload.get('order_id', 'N/A')}")
    lines.append(f"Canal : {payload.get('channel', 'TPV')}")
    if payload.get('customer_name'):
        lines.append(f"Cliente: {payload['customer_name']}")
    if payload.get('notes'):
        lines.append(f"Notas : {payload['notes']}")
    lines.append("-" * 32)

    total = 0.0
    for it in payload.get("items", []):
        qty = float(it.get("qty", 1))
        name = it.get("name", "Producto")
        price = float(it.get("price", 0))
        subtotal = qty * price
        total += subtotal
        lines.append(f"{qty:g} x {name}")
        lines.append(f"    {subtotal:,.2f} €")

    lines.append("-" * 32)
    lines.append(f"TOTAL: {total:,.2f} €")
    lines.append("-" * 32)
    lines.append("IVA INCLUIDO (10%)")
    lines.append("Gracias por su compra")
    lines.append("carbonesypollos.com")
    lines.append("\n\n") # Espacio para el corte de papel
    return "\n".join(lines)


def print_ticket(payload: dict) -> dict:
    """
    Retorna dict compatible API:
    {
      "ok": bool,
      "mode": "mock|bridge|escpos",
      "message": "...",
      "detail": ...
    }
    """
    mode = PRINT_MODE
    text = _ticket_text(payload)

    if mode == "mock":
        return {
            "ok": True,
            "mode": "mock",
            "message": "Impresión simulada (mock)",
            "ticket_text": text,
            "detail": {"preview": text}
        }

    if mode == "bridge":
        if requests is None:
            return {
                "ok": False,
                "mode": "bridge",
                "message": "requests no disponible para bridge",
                "ticket_text": text,
                "detail": None
            }
        try:
            resp = requests.post(
                LOCAL_PRINTER_URL,
                json={"ticket": text, "raw": payload},
                timeout=4
            )
            return {
                "ok": resp.ok,
                "mode": "bridge",
                "message": f"Bridge status {resp.status_code}",
                "ticket_text": text,
                "detail": {"response": resp.text[:500]}
            }
        except Exception as e:
            return {
                "ok": False,
                "mode": "bridge",
                "message": "Error enviando a bridge local",
                "ticket_text": text,
                "detail": str(e)
            }

    if mode == "escpos":
        # Placeholder seguro: evita romper en Render si no hay USB/driver
        return {
            "ok": False,
            "mode": "escpos",
            "message": "ESC/POS directo no habilitado en este entorno",
            "ticket_text": text,
            "detail": "Use PRINT_MODE=bridge en local con servicio de impresión."
        }

    return {
        "ok": False,
        "mode": mode,
        "message": "PRINT_MODE inválido",
        "ticket_text": text,
        "detail": "Valores válidos: mock|bridge|escpos"
    }
