import paramiko
import os
import sys

HOSTNAME = '113.30.148.104'
USERNAME = 'root'
PASSWORD = '633660438gK123'
REMOTE_PATH = '/root/carbones_y_pollos_tpv'
LOCAL_PATH = 'd:\\proyecto\\carbones_y_pollos_tpv'

COMMAND_START = f"""
pkill -f main.py
mkdir -p {REMOTE_PATH}
cd {REMOTE_PATH}
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install google-generativeai requests

# Parche de Migración Base de Datos SQLite Remota
python3 -c "
import sqlite3
import os
db_path = 'tpv_data.sqlite'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('PRAGMA table_info(pedidos)')
    columns = [col[1] for col in cur.fetchall()]
    new_cols = ['base_imponible_10', 'cuota_iva_10', 'base_imponible_21', 'cuota_iva_21']
    for col in new_cols:
        if col not in columns:
            cur.execute(f'ALTER TABLE pedidos ADD COLUMN {{col}} FLOAT DEFAULT 0.0')
    conn.commit()
    conn.close()
"

# Start server
nohup python3 main.py > server.log 2>&1 &
echo "Carbones TPV deployed, db patched, and restarted successfully on port 5001."
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
    
    for item in os.listdir(LOCAL_PATH):
        local_item = os.path.join(LOCAL_PATH, item)
        if os.path.isfile(local_item) and not item.endswith('.sqlite'): # Skip DB override
            sftp.put(local_item, f"{REMOTE_PATH}/{item}")
            print(f"Subido: {item}")
    
    # Static folder
    static_local = os.path.join(LOCAL_PATH, 'static')
    if os.path.isdir(static_local):
        for item in os.listdir(static_local):
            local_static = os.path.join(static_local, item)
            if os.path.isfile(local_static):
                sftp.put(local_static, f"{REMOTE_PATH}/static/{item}")
                print(f"Subido static: {item}")

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
