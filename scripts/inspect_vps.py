import paramiko

def inspect_vps():
    host = '113.30.148.104'
    user = 'root'
    password = '633660438gK1234'

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(host, username=user, password=password, timeout=10)
        print("[+] Conectado exitosamente al VPS Kamatera.")
        
        commands = [
            ("TPV Service", "systemctl status tpv.service"),
            ("Carbones-TPV Service", "systemctl status carbones-tpv.service")
        ]

        for name, cmd in commands:
            print(f"\n--- {name} ---")
            stdin, stdout, stderr = ssh.exec_command(cmd)
            out = stdout.read().decode().strip()
            err = stderr.read().decode().strip()
            if out:
                print(out)
            if err:
                print("ERROR:", err)
                
    except Exception as e:
        print(f"[-] Error conectando al VPS: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    inspect_vps()
