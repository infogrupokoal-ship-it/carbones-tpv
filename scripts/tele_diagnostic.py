import requests
import os

BASE_URL = "http://localhost:8000"

PORTALS = [
    "portal.html", "stats.html", "analytics.html", "inventario.html",
    "dashboard_produccion.html", "caja.html", "kds.html", "rrhh.html",
    "marketing.html", "reparto.html", "referidos.html", "escandallos.html",
    "auditoria.html", "settings.html", "iot.html", "franchise.html",
    "esg.html", "menu_engineering.html", "fleet_map.html", "erp.html",
    "commercial.html", "loyalty.html", "hardware.html", "mantenimiento.html",
    "crisis.html", "procurement.html", "delivery_aggregators.html"
]

def run_diagnostic():
    print("🔍 Starting Industrial Tele-Diagnostic v4.0...")
    
    # 1. Check Portals
    print("\n--- Portals Health ---")
    for portal in PORTALS:
        url = f"{BASE_URL}/static/{portal}"
        try:
            r = requests.get(url, timeout=2)
            status = "✅ OK" if r.status_code == 200 else f"❌ ERROR ({r.status_code})"
            print(f"{portal:30} {status}")
        except:
            print(f"{portal:30} ❌ UNREACHABLE")

    # 2. Check Core API
    print("\n--- API Health ---")
    endpoints = ["/health", "/api/stats/sales", "/api/inventory/status", "/api/notifications/"]
    for ep in endpoints:
        url = f"{BASE_URL}{ep}"
        try:
            r = requests.get(url, timeout=2)
            status = "✅ OK" if r.status_code == 200 else f"❌ ERROR ({r.status_code})"
            print(f"{ep:30} {status}")
        except:
            print(f"{ep:30} ❌ UNREACHABLE")

    print("\n🏁 Diagnostic Complete.")

if __name__ == "__main__":
    run_diagnostic()
