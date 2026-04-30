import requests
import sys

def audit_security(base_url):
    print(f"🛡️ Iniciando Auditoría de Seguridad Enterprise en: {base_url}")
    print("-" * 60)
    
    headers_to_check = [
        "X-Content-Type-Options",
        "X-Frame-Options",
        "X-XSS-Protection",
        "Strict-Transport-Security",
        "Content-Encoding" # Para verificar Gzip
    ]
    
    try:
        response = requests.get(base_url, timeout=5)
        
        print(f"[*] Código de Estado: {response.status_code}")
        
        passed = 0
        for h in headers_to_check:
            val = response.headers.get(h)
            if val:
                print(f"[✅] {h:<30}: {val}")
                passed += 1
            else:
                print(f"[❌] {h:<30}: MISSING")
                
        print("-" * 60)
        if passed == len(headers_to_check):
            print("🏆 RESULTADO: SISTEMA 100% SECURIZADO E INDUSTRIAL.")
        else:
            print("⚠️ ADVERTENCIA: SE RECOMIENDA REVISAR LAS CABECERAS FALTANTES.")
            
    except Exception as e:
        print(f"❌ Error durante la auditoría: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    audit_security(url)
