import paramiko
import os
import sys

if len(sys.argv) < 2:
    print("Uso: python deploy_android_tpv.py <IP_TABLET>")
    sys.exit(1)

HOSTNAME = sys.argv[1]
PORT = 8022
USERNAME = 'u0_a113' # Default Termux user on this device
PASSWORD = '633660438gk'

REMOTE_PATH = '/data/data/com.termux/files/home/carbones_y_pollos_tpv'
LOCAL_PATH = 'd:\\proyecto\\carbones_y_pollos_tpv'

BOOT_SCRIPT = """#!/data/data/com.termux/files/usr/bin/bash
termux-wake-lock
sshd
"""

WIDGET_SCRIPT = """#!/data/data/com.termux/files/usr/bin/bash
# Este script se ejecuta al tocar el Widget en la pantalla
cd ~/carbones_y_pollos_tpv
./arrancar_tpv.sh
"""

try:
    print(f"-> Conectando a la Tablet TPV ({HOSTNAME})...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOSTNAME, port=PORT, username=USERNAME, password=PASSWORD, timeout=10)
    
    print("-> Creando directorios base...")
    client.exec_command(f"mkdir -p {REMOTE_PATH}/static")
    client.exec_command("mkdir -p ~/.termux/boot")
    client.exec_command("mkdir -p ~/.shortcuts")
    
    print("-> Configurando Termux:Boot (Arranque Automático SSH)...")
    sftp = client.open_sftp()
    
    with sftp.open('.termux/boot/01-sshd.sh', 'w') as f:
        f.write(BOOT_SCRIPT)
    client.exec_command('chmod +x ~/.termux/boot/01-sshd.sh')

    print("-> Configurando Termux:Widget (Botón 1-Clic TPV)...")
    with sftp.open('.shortcuts/INICIAR_TPV.sh', 'w') as f:
        f.write(WIDGET_SCRIPT)
    client.exec_command('chmod +x ~/.shortcuts/INICIAR_TPV.sh')

    print("-> Subiendo archivos del proyecto...")
    ignored_extensions = ['.sqlite', '.sqlite-shm', '.sqlite-wal', '.pyc', '.png']
    ignored_dirs = ['venv', '__pycache__', '.git']

    for item in os.listdir(LOCAL_PATH):
        local_item = os.path.join(LOCAL_PATH, item)
        if os.path.isfile(local_item):
            if any(item.endswith(ext) for ext in ignored_extensions):
                continue
            try:
                sftp.put(local_item, f"{REMOTE_PATH}/{item}")
            except Exception as e:
                print(f"  Error al subir {item}: {e}")
                
    # Subir static
    static_local = os.path.join(LOCAL_PATH, 'static')
    if os.path.isdir(static_local):
        for item in os.listdir(static_local):
            local_static = os.path.join(static_local, item)
            if os.path.isfile(local_static):
                sftp.put(local_static, f"{REMOTE_PATH}/static/{item}")

    sftp.close()
    
    print("-> Dando permisos de ejecución...")
    client.exec_command(f'chmod +x {REMOTE_PATH}/*.sh')
    
    client.close()
    print("====================================================")
    print("¡ÉXITO! La TPV Android ha sido actualizada e instalada.")
    print("Por favor, en la tablet Android añade el Widget de Termux")
    print("a la pantalla de inicio y selecciona 'INICIAR_TPV.sh'.")
    print("====================================================")
    
except Exception as e:
    print(f"Error fatal conectando a la tablet: {e}")
    print("¿Está la tablet encendida, conectada a la red y con Termux abierto?")
    sys.exit(1)
