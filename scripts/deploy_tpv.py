import os
import sys

import paramiko

HOSTNAME = "113.30.148.104"
USERNAME = "root"
PASSWORD = "633660438gK1234"
REMOTE_PATH = "/root/carbones_y_pollos_tpv"
LOCAL_PATH = "d:\\proyecto\\carbones_y_pollos_tpv"

COMMAND_START = f"""
pkill -f main.py || true
mkdir -p {REMOTE_PATH}
cd {REMOTE_PATH}
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install google-generativeai requests

# Configurar Systemd
cp scripts/tpv.service /etc/systemd/system/tpv.service
systemctl daemon-reload
systemctl enable tpv
systemctl restart tpv

# Esperar a que inicie
sleep 3
python3 fractional_seeder.py

echo "Carbones TPV deployed, DB preserved, seeded, and restarted successfully via systemd (port 8000)."
"""

try:
    print(f"-> Conectando a {HOSTNAME}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOSTNAME, port=22, username=USERNAME, password=PASSWORD, timeout=30)

    # Ensure dir exists
    client.exec_command(f"mkdir -p {REMOTE_PATH}/static")

    print("-> Subiendo archivos vía SFTP...")
    sftp = client.open_sftp()

    def upload_recursive(local_folder, remote_folder):
        ignored_dirs = ["venv", ".git", "__pycache__", ".pytest_cache"]
        ignored_files = ["tpv_data.sqlite"] # No sobrescribir DB
        
        for item in os.listdir(local_folder):
            if item in ignored_dirs:
                continue
            
            local_path = os.path.join(local_folder, item)
            remote_path = f"{remote_folder}/{item}".replace("\\", "/")
            
            if os.path.isfile(local_path):
                if item in ignored_files or item.endswith(".sqlite-shm") or item.endswith(".sqlite-wal"):
                    continue
                sftp.put(local_path, remote_path)
                print(f"Subido: {remote_path}")
            elif os.path.isdir(local_path):
                try:
                    sftp.mkdir(remote_path)
                except Exception:
                    pass # Ya existe
                upload_recursive(local_path, remote_path)

    upload_recursive(LOCAL_PATH, REMOTE_PATH)
    sftp.close()

    print("-> Reiniciando servidor Carbones TPV...")
    stdin, stdout, stderr = client.exec_command(COMMAND_START)
    exit_status = stdout.channel.recv_exit_status()

    print("STDOUT:", stdout.read().decode())
    print("STDERR:", stderr.read().decode())

    client.close()
    print("-> Subida a VPS completada con éxito.")
except Exception as e:
    print(f"Error fatal: {e}")
    sys.exit(1)
