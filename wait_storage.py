import paramiko
import time
client=paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('192.168.1.154', port=8022, username='u0_a113', password='633660438gk', timeout=5)

for i in range(30):
    stdin, stdout, stderr = client.exec_command('ls -d ~/storage/downloads')
    out = stdout.read().decode().strip()
    if 'downloads' in out.lower() or out:
        print("Storage found!")
        client.exec_command('cp /data/data/com.termux/files/home/termux_boot.apk ~/storage/downloads/')
        break
    time.sleep(2)
print("Done")
