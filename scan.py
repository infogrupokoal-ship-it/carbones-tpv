import socket
import concurrent.futures

def scan(p):
    s = socket.socket()
    s.settimeout(0.3)
    res = s.connect_ex(('192.168.1.154', p))
    s.close()
    return p if res == 0 else None

with concurrent.futures.ThreadPoolExecutor(max_workers=500) as e:
    open_ports = [p for p in e.map(scan, range(1, 45000)) if p]

print('Puertos abiertos en 192.168.1.154:', open_ports)
