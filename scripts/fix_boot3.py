import time

import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(
    "192.168.1.154", port=8022, username="u0_a113", password="633660438gk", timeout=5
)


def run_cmd(cmd):
    stdin, stdout, stderr = client.exec_command(cmd)
    return stdout.read().decode().strip() + stderr.read().decode().strip()


print("--- UPDATING BOOT SCRIPT ---")
boot_script = """#!/data/data/com.termux/files/usr/bin/bash
termux-wake-lock
sshd
cd ~/carbones-tpv
# Usar el python del sistema termux o de venv si existe
if [ -d "venv" ]; then
    source venv/bin/activate
fi
nohup python local_printer_bridge.py > bridge.log 2>&1 &
"""

# Uploading script via SFTP
sftp = client.open_sftp()
with sftp.open(".termux/boot/01-start-tpv.sh", "w") as f:
    f.write(boot_script)
sftp.close()

run_cmd("chmod +x ~/.termux/boot/01-start-tpv.sh")

print("--- KILLING OLD PROCESS ---")
run_cmd("pkill -f local_printer_bridge.py")

print("--- STARTING NEW PROCESS ---")
run_cmd("~/.termux/boot/01-start-tpv.sh")

time.sleep(3)
print("--- CHECKING NEW LOGS ---")
print(run_cmd("cat ~/carbones-tpv/bridge.log"))
