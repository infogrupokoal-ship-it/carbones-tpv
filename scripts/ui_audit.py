import re
from pathlib import Path

def audit_ui(static_dir="static"):
    print(f"[INFO] Iniciando Auditoria de UI en: {static_dir}")
    
    html_files = list(Path(static_dir).rglob("*.html"))
    broken_links = []
    
    # Expresion regular para encontrar enlaces en HTML (href y onclick con location.href)
    link_patterns = [
        re.compile(r'href=["\'](?!http|https|#)([^"\']+)["\']'),
        re.compile(r'location\.href\s*=\s*["\'](?!http|https|#)([^"\']+)["\']')
    ]
    
    # Rutas permitidas que no son archivos estaticos (API, Docs)
    allowed_backend_routes = ["/api", "/docs", "/redoc", "/health"]
    
    for html_file in html_files:
        try:
            with open(html_file, "r", encoding="utf-8") as f:
                content = f.read()
                
                found_links = []
                for pattern in link_patterns:
                    found_links.extend(pattern.findall(content))
                
                for link in found_links:
                    # Ignorar rutas de backend
                    if any(link.startswith(route) for route in allowed_backend_routes):
                        continue
                        
                    # Normalizar ruta
                    if link.startswith("/static/"):
                        rel_link = link.replace("/static/", "", 1)
                        target_path = Path(static_dir) / rel_link
                    elif link.startswith("/"):
                        # Asumir que es relativo a la raiz si empieza por /
                        target_path = Path(static_dir) / link.lstrip("/")
                    else:
                        # Relativo al archivo actual
                        target_path = html_file.parent / link
                    
                    # Quitar parametros de busqueda o fragmentos
                    target_path_str = str(target_path).split("?")[0].split("#")[0]
                    target_path = Path(target_path_str)
                    
                    if not target_path.exists():
                        broken_links.append((html_file.name, link, str(target_path)))
        except Exception as e:
            print(f"[WARN] No se pudo leer {html_file.name}: {e}")
    
    if broken_links:
        print(f"[ERROR] Se encontraron {len(broken_links)} enlaces rotos:")
        for file, link, target in broken_links:
            print(f"  - En {file}: '{link}' -> No existe {target}")
    else:
        print("[SUCCESS] Navegacion integra. No se detectaron enlaces rotos.")

if __name__ == "__main__":
    audit_ui()
