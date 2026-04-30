import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(
    "192.168.1.154", port=8022, username="u0_a113", password="633660438gk", timeout=5
)

print("Taking screenshot...")
stdin, stdout, stderr = client.exec_command(
    "/system/bin/screencap -p > /data/data/com.termux/files/home/screen.png"
)
stdout.channel.recv_exit_status()  # wait for it to finish
err = stderr.read().decode()
if err:
    print("ERR:", err)

print("Downloading screenshot...")
sftp = client.open_sftp()
sftp.get("/data/data/com.termux/files/home/screen.png", "screen.png")
print("Done!")
