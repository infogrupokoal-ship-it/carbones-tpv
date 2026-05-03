
import paramiko
import sys
import os

def audit_vps():
    hostname = "113.30.148.104"
    username = "root"
    password = "633660438gK1234"
    
    print(f"--- INICIANDO AUDITORIA INDUSTRIAL VPS: {hostname} ---")
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"[1/5] Conectando como {username}...")
        client.connect(hostname, username=username, password=password, timeout=10)
        print("[OK] Conexion establecida satisfactoriamente.")
        
        # 1. Información del Sistema
        print("[2/5] Recopilando telemetria del sistema...")
        stdin, stdout, stderr = client.exec_command("uname -a && uptime && df -h /")
        print("--- OS & DISK ---")
        print(stdout.read().decode())
        
        # 2. Verificación de Entorno Python
        print("[3/5] Verificando entorno de ejecucion...")
        stdin, stdout, stderr = client.exec_command("python3 --version && pip3 --version")
        print("--- PYTHON ---")
        print(stdout.read().decode())
        
        # 3. Verificación de Carpeta de Proyecto e Integridad Git
        print("[4/5] Auditando directorio del proyecto...")
        project_dir = "/root/carbones_y_pollos_tpv"
        cmd = f"if [ -d '{project_dir}' ]; then cd {project_dir} && git status && ls -F; else echo '[ERROR] Carpeta no encontrada'; fi"
        stdin, stdout, stderr = client.exec_command(cmd)
        print("--- PROJECT STATE ---")
        print(stdout.read().decode())
        
        # 4. Auditoría de Seguridad SSH
        print("[5/5] Analizando configuracion de seguridad SSH...")
        stdin, stdout, stderr = client.exec_command("grep -E 'PermitRootLogin|PasswordAuthentication' /etc/ssh/sshd_config")
        print("--- SSH CONFIG ---")
        print(stdout.read().decode())
        
        # 5. Puertos Activos
        print("[EXTRA] Verificando puertos en escucha (TPV/API)...")
        stdin, stdout, stderr = client.exec_command("netstat -tuln | grep -E '5001|8000|22'")
        print("--- NETWORK PORTS ---")
        print(stdout.read().decode())

    except Exception as e:
        print(f"[ERROR] FALLO CRITICO EN AUDITORIA: {e}")
    finally:
        client.close()
        print("--- FIN DE AUDITORIA ---")

if __name__ == "__main__":
    audit_vps()
