import concurrent.futures
import re
import socket
import subprocess

out = subprocess.check_output("arp -a").decode("cp1252", errors="ignore")
ips = list(set(re.findall(r"192\.168\.\d+\.\d+", out)))


def s(ip, port):
    sk = socket.socket()
    sk.settimeout(0.3)
    r = sk.connect_ex((ip, port))
    sk.close()
    return ip if r == 0 else None


with concurrent.futures.ThreadPoolExecutor(100) as e:
    found8022 = [ip for ip in e.map(lambda i: s(i, 8022), ips) if ip]
    found5001 = [ip for ip in e.map(lambda i: s(i, 5001), ips) if ip]

print("8022:", found8022)
print("5001:", found5001)
