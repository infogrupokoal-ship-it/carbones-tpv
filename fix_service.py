import paramiko
import time

new_service = """[Unit]
Description=Gunicorn instance to serve TPV Carbones y Pollos Enterprise
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/carbones_tpv
Environment="PATH=/opt/carbones_tpv/venv/bin"
EnvironmentFile=/opt/carbones_tpv/.env

ExecStart=/opt/carbones_tpv/venv/bin/gunicorn --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --access-logfile /var/log/tpv/access.log --error-logfile /var/log/tpv/error.log backend.main:app

Restart=always
RestartSec=5
KillSignal=SIGQUIT
Type=notify
NotifyAccess=all

[Install]
WantedBy=multi-user.target
"""

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('113.30.148.104', port=22, username='root', password='633660438Gk123')

sftp = client.open_sftp()
with sftp.file('/etc/systemd/system/tpv.service', 'w') as f:
    f.write(new_service)
sftp.close()

client.exec_command('systemctl daemon-reload')
time.sleep(1)
client.exec_command('systemctl restart tpv.service')
time.sleep(3)

stdin, stdout, stderr = client.exec_command('systemctl status tpv.service --no-pager')
print(stdout.read().decode('utf-8', errors='ignore'))
client.close()
