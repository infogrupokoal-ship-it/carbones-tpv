import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(
    "192.168.1.154", port=8022, username="u0_a113", password="633660438gk", timeout=5
)


def run_cmd(cmd):
    print("Running:", cmd)
    stdin, stdout, stderr = client.exec_command(cmd)
    exit_status = stdout.channel.recv_exit_status()
    print("OUT:", stdout.read().decode())
    print("ERR:", stderr.read().decode())
    print("Exit:", exit_status)


# Download APKs
run_cmd(
    "curl -L -o /data/data/com.termux/files/home/termux_boot.apk https://f-droid.org/repo/com.termux.boot_1000.apk"
)
run_cmd(
    "curl -L -o /data/data/com.termux/files/home/anydesk.apk https://download.anydesk.com/anydesk.apk"
)

# Attempt silent install
print("Attempting silent pm install...")
run_cmd("/system/bin/pm install /data/data/com.termux/files/home/termux_boot.apk")

# Also trigger termux-open as fallback
print("Triggering visual install dialogs...")
run_cmd("termux-open /data/data/com.termux/files/home/termux_boot.apk")
run_cmd("termux-open /data/data/com.termux/files/home/anydesk.apk")
