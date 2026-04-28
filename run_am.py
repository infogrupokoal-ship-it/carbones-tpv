import paramiko
client=paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('192.168.1.154', port=8022, username='u0_a113', password='633660438gk', timeout=5)

def run_cmd(cmd):
    stdin, stdout, stderr = client.exec_command(cmd)
    print('OUT:', stdout.read().decode())
    print('ERR:', stderr.read().decode())

run_cmd('/system/bin/am start -a android.intent.action.VIEW -d "market://details?id=com.anydesk.anydeskandroid"')
run_cmd('/system/bin/am start -a android.intent.action.VIEW -d "market://details?id=com.termux.boot"')
run_cmd('/system/bin/am start -a android.intent.action.VIEW -d "market://details?id=com.android.chrome"')
