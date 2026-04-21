import sys
from fastapi.testclient import TestClient
from main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Categoria, Producto, Pedido

client = TestClient(app)

def run_spider():
    print("--- INICIANDO SPIDER TEST PARA CARBONS Y POLLOS TPV ---")
    
    # We will test all GET routes that don't need parameters first
    passed = 0
    failed = []
    dynamic_passed = 0
    dynamic_failed = []
    
    routes = app.routes
    for route in routes:
        if not hasattr(route, "methods"):
            continue
            
        if "GET" in route.methods:
            path = route.path
            
            # Simple static routes
            if "{" not in path:
                try:
                    response = client.get(path)
                    if response.status_code >= 500:
                        failed.append({'url': path, 'status': response.status_code})
                    else:
                        passed += 1
                except Exception as e:
                    failed.append({'url': path, 'error': str(e)[:80]})
            else:
                # Dynamic routes processing (mocking simple IDs)
                url = path.replace("{categoria_id}", "1")
                url = url.replace("{pedido_id}", "1")
                try:
                    response = client.get(url)
                    if response.status_code >= 500:
                        dynamic_failed.append({'url': url, 'status': response.status_code})
                    else:
                        dynamic_passed += 1
                except Exception as e:
                    dynamic_failed.append({'url': url, 'error': str(e)[:80]})

    print("--- RESUMEN RUTAS ESTÁTICAS (TPV) ---")
    print(f"Probadas: {passed + len(failed)}")
    print(f"Éxitos: {passed}")
    print(f"Fallos: {len(failed)}")
    if failed:
        for f in failed:
            print(f)
            
    print("--- RESUMEN RUTAS DINÁMICAS (TPV) ---")
    print(f"Probadas: {dynamic_passed + len(dynamic_failed)}")
    print(f"Éxitos: {dynamic_passed}")
    print(f"Fallos: {len(dynamic_failed)}")
    if dynamic_failed:
        for f in dynamic_failed:
            print(f)

run_spider()
