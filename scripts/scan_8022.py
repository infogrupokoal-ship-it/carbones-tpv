import concurrent.futures
import socket


def check(ip):
    try:
        s = socket.socket()
        s.settimeout(0.5)
        if s.connect_ex((ip, 8022)) == 0:
            return ip
    except Exception:
        pass
    return None


ips = [f"192.168.1.{i}" for i in range(1, 255)]
with concurrent.futures.ThreadPoolExecutor(100) as executor:
    found = [ip for ip in executor.map(check, ips) if ip]

print(f"Found 8022 on: {found}")
