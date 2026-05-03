import paramiko

def cleanup_vps():
    host = '113.30.148.104'
    user = 'root'
    password = '633660438gK1234'

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(host, username=user, password=password, timeout=10)
        print("[+] Conectado exitosamente al VPS Kamatera para limpieza.")
        
        commands = [
            ("Deteniendo servicio conflictivo (carbones-tpv.service)", "systemctl stop carbones-tpv.service"),
            ("Deshabilitando servicio conflictivo (carbones-tpv.service)", "systemctl disable carbones-tpv.service"),
            ("Matando procesos zombie python main.py", "pkill -f 'python3 main.py' || true"),
            ("Reiniciando servicio oficial (tpv.service)", "systemctl restart tpv.service"),
            ("Estado final de tpv.service", "systemctl status tpv.service --no-pager | head -n 15")
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
                
        print("\n✅ Limpieza de VPS completada.")
    except Exception as e:
        print(f"[-] Error conectando al VPS: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    cleanup_vps()
