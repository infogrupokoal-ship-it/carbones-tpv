import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(
    "192.168.1.154", port=8022, username="u0_a113", password="633660438gk", timeout=5
)


def run_cmd(cmd):
    print(">", cmd)
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode()
    if out:
        print("OUT:", out.strip())
    err = stderr.read().decode()
    if err:
        print("ERR:", err.strip())


run_cmd("pm list packages | grep anydesk")
run_cmd("pm list packages | grep termux.boot")
run_cmd("pm list packages | grep chrome")
run_cmd("ls -la ~/.termux/boot/start_tpv.sh")
run_cmd("cat ~/.termux/boot/start_tpv.sh")
