import requests
import sys
import time

# Script de Validación de Integridad (Smoke Test)
# Carbones y Pollos TPV - Enterprise v2.5

BASE_URL = "http://localhost:8000" if len(sys.argv) < 2 else sys.argv[1]

endpoints = [
    {"path": "/health", "expected_status": 200, "name": "Health Check"},
    {"path": "/api/admin/dashboard/kpis", "expected_status": 200, "name": "Dashboard Analytics"},
    {"path": "/api/orders/today", "expected_status": 200, "name": "Real-time Orders"},
    {"path": "/static/index.html", "expected_status": 200, "name": "Enterprise Hub"},
    {"path": "/api/rrhh/fichajes", "expected_status": 200, "name": "HR Portal Data"}
]

def run_smoke_test():
    print(f"🔍 Iniciando Smoke Test en: {BASE_URL}")
    print("-" * 50)
    
    all_passed = True
    for ep in endpoints:
        try:
            start_time = time.time()
            response = requests.get(f"{BASE_URL}{ep['path']}", timeout=5)
            latency = time.time() - start_time
            
            status = "✅ PASSED" if response.status_code == ep['expected_status'] else "❌ FAILED"
            if response.status_code != ep['expected_status']:
                all_passed = False
            
            print(f"{status} | {ep['name']:<20} | Status: {response.status_code} | Latency: {latency:.4f}s")
            
        except Exception as e:
            print(f"❌ ERROR  | {ep['name']:<20} | Exception: {str(e)}")
            all_passed = False

    print("-" * 50)
    if all_passed:
        print("🏆 RESULTADO: SISTEMA 100% OPERATIVO Y PROFESIONAL.")
    else:
        print("⚠️ RESULTADO: SE DETECTARON FALLOS EN LA INFRAESTRUCTURA.")
        sys.exit(1)

if __name__ == "__main__":
    run_smoke_test()
