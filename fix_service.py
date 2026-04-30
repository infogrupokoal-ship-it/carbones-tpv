import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('113.30.148.104', port=22, username='root', password='633660438Gk123')

service_file = """[Unit]
Description=Gunicorn instance to serve TPV Carbones y Pollos Enterprise
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/root/carbones_y_pollos_tpv
Environment="PATH=/root/carbones_y_pollos_tpv/venv/bin"
Environment="GOOGLE_API_KEY="

ExecStart=/root/carbones_y_pollos_tpv/venv/bin/gunicorn --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 backend.main:app

Restart=always
RestartSec=5
KillSignal=SIGQUIT

[Install]
WantedBy=multi-user.target
"""

stdin, stdout, stderr = client.exec_command('cat > /etc/systemd/system/tpv.service', get_pty=False)
stdin.write(service_file.encode('utf-8'))
stdin.close()
# Wait for the file to be written
stdout.channel.recv_exit_status()

# Make sure venv and gunicorn are correctly set up
# We also need to run `pip install -r requirements.txt` just in case the previous script failed.
print("Reinstalling requirements just in case...")
stdin, stdout, stderr = client.exec_command('cd /root/carbones_y_pollos_tpv && /root/carbones_y_pollos_tpv/venv/bin/pip install -r requirements.txt')
print(stdout.read().decode())
print(stderr.read().decode())

print("Reloading systemd and restarting...")
client.exec_command('systemctl daemon-reload')
client.exec_command('systemctl restart tpv.service')

print("Checking status...")
import time
time.sleep(3)
stdin, stdout, stderr = client.exec_command('systemctl status tpv.service')
print(stdout.read().decode())
client.close()
print("DONE")
