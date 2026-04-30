import requests
import os
import time
from datetime import datetime

# CLI Maestro de Administración - Carbones y Pollos TPV
# Diseñado para administradores de VPS

API_URL = "http://localhost:8000/api/admin"

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_stats():
    try:
        res = requests.get(f"{API_URL}/dashboard/kpis", timeout=2)
        if res.ok:
            return res.json()
    except:
        return None

def main_loop():
    while True:
        data = get_stats()
        clear()
        
        print("\033[93m" + "="*60)
        print("    🔥 CARBONES Y POLLOS TPV - MONITOR DE SISTEMA 🔥")
        print("="*60 + "\033[0m")
        
        if data:
            kpis = data['kpis']
            print(f"🕒 Hora: {datetime.now().strftime('%H:%M:%S')}    | 🔌 Estado: ONLINE")
            print("-" * 60)
            print(f"💰 VENTAS HOY:    \033[92m{kpis['ventas_hoy']:.2f}€\033[0m")
            print(f"📦 PEDIDOS B2C:   \033[94m{kpis['pedidos_b2c']}\033[0m")
            print(f"📉 MERMAS (EST):  \033[91m{kpis['coste_mermas']:.2f}€\033[0m")
            print(f"⭐ RATING MEDIO:  \033[93m{kpis['avg_rating']}\033[0m")
            print("-" * 60)
            
            print("\033[90mÚLTIMAS RESEÑAS:\033[0m")
            for r in data['reviews'][:2]:
                print(f"  • {r['cliente_nombre']}: {r['comentario'][:40]}...")
        else:
            print("\033[91m⚠️ ERROR: SERVIDOR BACKEND OFFLINE O NO ALCANZABLE\033[0m")
            print("Intentando reconectar en 5 segundos...")
        
        print("\n\033[90mPresiona Ctrl+C para salir.\033[0m")
        time.sleep(5)

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        print("\nCerrando monitor.")
