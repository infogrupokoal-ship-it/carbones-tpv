import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(
    "192.168.1.154", port=8022, username="u0_a113", password="633660438gk", timeout=5
)

script = """#!/data/data/com.termux/files/usr/bin/bash
termux-wake-lock
sshd
cd ~/carbones-tpv
source venv/bin/activate
nohup python local_printer_bridge.py > bridge.log 2>&1 &
"""

client.exec_command("rm -f ~/.termux/boot/*")

stdin, stdout, stderr = client.exec_command("cat > ~/.termux/boot/01-start-tpv.sh")
stdin.write(script)
stdin.close()

client.exec_command("chmod +x ~/.termux/boot/01-start-tpv.sh")
client.exec_command("~/.termux/boot/01-start-tpv.sh")
print("Done")
