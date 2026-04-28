import socket
import concurrent.futures
import subprocess
import sys

def check_port(ip):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.5)
    try:
        if s.connect_ex((ip, 8022)) == 0:
            return ip
    except:
        pass
    finally:
        s.close()
    return None

print("Buscando TPV Android en la red local (puerto 8022)...")
ips_to_scan = [f"192.168.1.{i}" for i in range(1, 255)] + [f"192.168.0.{i}" for i in range(1, 255)]

found_ips = []
with concurrent.futures.ThreadPoolExecutor(max_workers=200) as executor:
    results = executor.map(check_port, ips_to_scan)
    for ip in results:
        if ip:
            found_ips.append(ip)

if not found_ips:
    print("Error: No se ha encontrado ninguna TPV Android con Termux abierto en el puerto 8022 en la red local.")
    sys.exit(1)

target_ip = found_ips[0]
print(f"TPV Android encontrada en la IP: {target_ip}")
print("Iniciando despliegue automático...")

# Run deploy script
subprocess.run([sys.executable, "deploy_android_tpv.py", target_ip])
