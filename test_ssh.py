import paramiko
import json

host = '113.30.148.104'
user = 'root'
passwords = ['633660438gK123', '633660438Gk!123', '633660438Gk123', '633660438gk!123', '633660438']

for p in passwords:
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print(f"Trying password {p}...")
        ssh.connect(host, username=user, password=p, timeout=5)
        print(f"SUCCESS with password {p}")
        ssh.close()
        break
    except Exception as e:
        print(f"FAILED: {e}")

