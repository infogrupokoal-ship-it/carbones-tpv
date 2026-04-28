import paramiko
import time

try:
    print('Conectando a la tablet...')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect('192.168.1.154', port=8022, username='u0_a113', password='633660438gk', timeout=10)

    print('Generando nuevo script de arranque...')
    boot_script = """#!/data/data/com.termux/files/usr/bin/bash
termux-wake-lock
sshd
cd ~/carbones-tpv
if [ -d "venv" ]; then
    source venv/bin/activate
fi
nohup python local_printer_bridge.py > bridge.log 2>&1 &
"""
    
    sftp = client.open_sftp()
    with sftp.open('.termux/boot/01-start-tpv.sh', 'w') as f:
        f.write(boot_script)
    sftp.close()

    print('Aplicando permisos y reiniciando puente...')
    client.exec_command('chmod +x ~/.termux/boot/01-start-tpv.sh')
    client.exec_command('pkill -f local_printer_bridge.py')
    time.sleep(2)
    client.exec_command('~/.termux/boot/01-start-tpv.sh')
    print('¡Puente de impresión actualizado e iniciado correctamente en la tablet!')

except Exception as e:
    print(f'Error: {e}')
finally:
    client.close()
