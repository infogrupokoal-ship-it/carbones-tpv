import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(
    "192.168.1.154", port=8022, username="u0_a113", password="633660438gk", timeout=5
)


def run_cmd(cmd):
    stdin, stdout, stderr = client.exec_command(cmd)
    return stdout.read().decode().strip()


print("Termux packages:")
print(run_cmd("pm list packages | grep -i termux"))

print("\nChrome/Browser packages:")
print(run_cmd("pm list packages | grep -i chrome"))
print(run_cmd("pm list packages | grep -i browser"))
