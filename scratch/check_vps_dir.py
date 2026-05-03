
import paramiko

def check_dir():
    hostname = "113.30.148.104"
    username = "root"
    password = "633660438gK1234"
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, username=username, password=password)
    
    stdin, stdout, stderr = client.exec_command("ls -la /root")
    print("--- /root CONTENTS ---")
    print(stdout.read().decode())
    
    stdin, stdout, stderr = client.exec_command("ls -la /root/carbones_y_pollos_tpv")
    print("--- PROJECT DIR CONTENTS ---")
    print(stdout.read().decode())
    print("--- ERRORS ---")
    print(stderr.read().decode())
    
    client.close()

if __name__ == "__main__":
    check_dir()
