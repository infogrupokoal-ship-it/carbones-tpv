import paramiko
import sys

def check_vps():
    host = '113.30.148.104'
    user = 'root'
    password = '633660438gK1234'
    
    try:
        print(f"Connecting to {host}...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=user, password=password, timeout=10)
        print("Connected successfully!")
        
        commands = [
            "echo '--- OS Version ---'",
            "uname -a",
            "lsb_release -a",
            "echo '--- Directory Content ---'",
            "ls -la /root/carbones_y_pollos_tpv",
            "echo '--- Git Status ---'",
            "cd /root/carbones_y_pollos_tpv && git status",
            "echo '--- Running Processes (Uvicorn/Gunicorn/Python) ---'",
            "ps aux | grep -E 'uvicorn|gunicorn|python3 main.py' | grep -v grep",
            "echo '--- Port 5001 status ---'",
            "netstat -tuln | grep 5001"
        ]
        
        for cmd in commands:
            stdin, stdout, stderr = ssh.exec_command(cmd)
            out = stdout.read().decode('utf-8')
            err = stderr.read().decode('utf-8')
            if out: print(out.strip())
            if err: print(f"Error: {err.strip()}")
            
        ssh.close()
    except Exception as e:
        print(f"Failed to connect or execute: {e}")

if __name__ == '__main__':
    check_vps()
