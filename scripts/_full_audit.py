"""
full_audit.py - Auditoría completa del sistema de ventas en producción
"""
import urllib.request
import json
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE = "https://carbones-tpv.onrender.com"

def get(path, timeout=25):
    try:
        url = f"{BASE}{path}"
        req = urllib.request.Request(url, headers={'User-Agent': 'TPV-Auditor/1.0'})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read()
            ct = r.headers.get('Content-Type', '')
            if 'json' in ct:
                return r.status, json.loads(body)
            return r.status, body[:500].decode('utf-8', 'replace')
    except Exception as e:
        return 0, str(e)

print("=" * 65)
print("AUDITORIA COMPLETA TPV ONLINE")
print("=" * 65)

# 1. Health
s, d = get("/health")
print(f"\n[1] /health → {s} | version: {d.get('version','?') if isinstance(d,dict) else 'ERROR'}")
if isinstance(d, dict):
    print(f"    status: {d.get('status')} | uptime: {d.get('uptime_seconds',0):.0f}s")

# 2. Productos
s, d = get("/api/productos/?limit=200")
if isinstance(d, list):
    prods = d
elif isinstance(d, dict):
    prods = d.get('value', d.get('items', []))
else:
    prods = []
print(f"\n[2] /api/productos/ → {s} | Total: {len(prods)}")
with_price = [p for p in prods if (p.get('precio') or 0) > 0]
zero_price = [p for p in prods if (p.get('precio') or 0) == 0]
print(f"    Con precio > 0: {len(with_price)}")
print(f"    Con precio = 0: {len(zero_price)}")
cats = {}
for p in with_price:
    c = p.get('categoria', 'Sin cat')
    cats[c] = cats.get(c, 0) + 1
for cat, n in sorted(cats.items(), key=lambda x: -x[1]):
    print(f"      {n:3d}  {cat[:50]}")

# 3. Pedidos
s, d = get("/api/orders/?limit=50")
orders = d if isinstance(d, list) else d.get('value', []) if isinstance(d, dict) else []
print(f"\n[3] /api/orders/ → {s} | Pedidos: {len(orders)}")
if orders:
    estados = {}
    for o in orders:
        e = o.get('estado', '?')
        estados[e] = estados.get(e, 0) + 1
    for e, n in estados.items():
        print(f"      {e}: {n}")

# 4. Endpoints críticos de venta
endpoints = [
    ("/api/orders/", "POST pedido B2C"),
    ("/api/ai/chat", "Chat Carbonito"),
    ("/api/telemetry/advanced", "Telemetría"),
    ("/api/ai/status", "AI Status"),
]
print("\n[4] Endpoints críticos:")
for path, desc in endpoints:
    s, d = get(path)
    ok = "OK" if s in [200, 405, 422] else f"ERROR {s}"
    print(f"    {ok:10} {path:35} {desc}")

# 5. Páginas HTML
pages = [
    ("/", "Tienda B2C (raíz)"),
    ("/static/index.html", "Tienda B2C"),
    ("/static/tpv.html", "TPV Mostrador"),
    ("/static/kiosko.html", "Kiosko"),
    ("/static/caja.html", "Caja / Cola"),
    ("/static/cocina.html", "Cocina"),
    ("/static/portal.html", "Portal admin"),
    ("/static/login.html", "Login"),
    ("/static/dashboard.html", "Dashboard"),
]
print("\n[5] Páginas HTML:")
for path, desc in pages:
    s, d = get(path)
    size = len(d) if isinstance(d, str) else len(str(d))
    ok = "OK" if s == 200 else f"ERR {s}"
    print(f"    {ok:8} {s:4} {size:6}B  {path:30} {desc}")

# 6. Intentar crear un pedido de prueba
print("\n[6] Test POST /api/orders/ (pedido de prueba):")
try:
    test_payload = json.dumps({
        "items": [{"producto_id": with_price[0]['id'], "cantidad": 1}] if with_price else [],
        "origen": "TEST",
        "estado_inicial": "PENDIENTE",
        "metodo_pago": "EFECTIVO",
        "notas_cliente": "TEST AUDITORIA - IGNORAR",
        "metodo_envio": "LOCAL"
    }).encode()
    req = urllib.request.Request(
        f"{BASE}/api/orders/",
        data=test_payload,
        headers={'Content-Type': 'application/json', 'User-Agent': 'TPV-Auditor'},
        method='POST'
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        result = json.loads(r.read())
        print(f"    OK! Pedido creado: #{result.get('numero_ticket','?')} | Estado: {result.get('estado','?')}")
        print(f"    ID: {result.get('id','?')[:16]}...")
except Exception as e:
    print(f"    ERROR: {e}")

print(f"\n{'=' * 65}")
print("RESUMEN:")
print(f"  Productos visibles (precio>0): {len(with_price)}")
print(f"  Categorias: {len(cats)}")
print(f"  Pedidos en BD: {len(orders)}")
