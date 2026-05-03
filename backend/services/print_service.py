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
    lines.append("CARBONES Y POLLOS")
    lines.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    lines.append("-" * 32)
    lines.append(f"Pedido: {payload.get('order_id', 'N/A')}")
    lines.append(f"Canal : {payload.get('channel', 'TPV')}")
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
    lines.append("Gracias por su compra")
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

    if mode == "mock":
        return {
            "ok": True,
            "mode": "mock",
            "message": "Impresión simulada (mock)",
            "detail": {"preview": _ticket_text(payload)}
        }

    if mode == "bridge":
        if requests is None:
            return {
                "ok": False,
                "mode": "bridge",
                "message": "requests no disponible para bridge",
                "detail": None
            }
        try:
            resp = requests.post(
                LOCAL_PRINTER_URL,
                json={"ticket": _ticket_text(payload), "raw": payload},
                timeout=4
            )
            return {
                "ok": resp.ok,
                "mode": "bridge",
                "message": f"Bridge status {resp.status_code}",
                "detail": {"response": resp.text[:500]}
            }
        except Exception as e:
            return {
                "ok": False,
                "mode": "bridge",
                "message": "Error enviando a bridge local",
                "detail": str(e)
            }

    if mode == "escpos":
        # Placeholder seguro: evita romper en Render si no hay USB/driver
        return {
            "ok": False,
            "mode": "escpos",
            "message": "ESC/POS directo no habilitado en este entorno",
            "detail": "Use PRINT_MODE=bridge en local con servicio de impresión."
        }

    return {
        "ok": False,
        "mode": mode,
        "message": "PRINT_MODE inválido",
        "detail": "Valores válidos: mock|bridge|escpos"
    }
