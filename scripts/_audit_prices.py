import urllib.request, json, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

url = "https://carbones-tpv.onrender.com/api/productos/?limit=200"
with urllib.request.urlopen(url, timeout=20) as r:
    data = json.loads(r.read())

prods = data if isinstance(data, list) else data.get("value", [])
with_price = [p for p in prods if (p.get("precio") or 0) > 0]
zero_price = [p for p in prods if (p.get("precio") or 0) == 0]

print(f"Total productos: {len(prods)}")
print(f"Con precio > 0: {len(with_price)}")
print(f"Con precio = 0: {len(zero_price)}")

# Also check orders
url2 = "https://carbones-tpv.onrender.com/api/orders/?limit=20"
with urllib.request.urlopen(url2, timeout=20) as r2:
    orders = json.loads(r2.read())
print(f"\nPedidos totales (ultimos 20): {len(orders)}")

print("\n=== PRODUCTOS (nombre, precio, cat) ===")
for p in with_price:
    cat = (p.get("categoria") or "?").encode('ascii', 'replace').decode()
    nombre = p["nombre"].encode('ascii', 'replace').decode()
    print(f"  {p['precio']:6.2f}  |  {nombre[:35]:<35}  |  {cat}")

if zero_price:
    print(f"\n=== SIN PRECIO ===")
    for p in zero_price[:15]:
        nombre = p["nombre"].encode('ascii', 'replace').decode()
        cat = (p.get("categoria") or "?").encode('ascii', 'replace').decode()
        print(f"  {nombre[:40]} | {cat}")
