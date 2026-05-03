import json

import paramiko

host = "113.30.148.104"
user = "root"
password = "633660438gK1234"
waha_key = "1060705b0a574d1fbc92fa10a2b5aca7"

# Read the plan
with open(
    r"d:\proyecto\carbones_y_pollos_tpv\PLAN_ESTRATEGICO.md", "r", encoding="utf-8"
) as f:
    plan_text = f.read()

# Add a greeting
mensaje = (
    "🤖 *Hola, soy tu IA de la TPV (Gemini).* 🤖\n\nAquí tienes el Plan Estratégico y las instrucciones para el local, enviado desde el nodo de comunicaciones de Grupo Koal como pediste:\n\n"
    + plan_text
)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print(f"[*] Conectando SSH a {host}...")
    ssh.connect(host, username=user, password=password, timeout=10)

    payload = {"session": "default", "chatId": "34604864187@c.us", "text": mensaje}

    # We will save the payload into a temp file on the VPS to avoid curl quote escaping hell
    sftp = ssh.open_sftp()
    with sftp.file("/tmp/wa_payload.json", "w") as f:
        f.write(json.dumps(payload))
    sftp.close()

    cmd = f'curl -s -X POST "http://127.0.0.1:3000/api/sendText" -H "accept: application/json" -H "X-Api-Key: {waha_key}" -H "Content-Type: application/json" -d "@/tmp/wa_payload.json"'

    print("[*] Ejecutando Comando Curl a Port 3000...")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    res_3000 = stdout.read().decode("utf-8")
    err_3000 = stderr.read().decode("utf-8")

    print("Respuesta 3000:", res_3000)
    if err_3000:
        print("Error 3000:", err_3000)

    if (
        "Unauthorized" in res_3000
        or "Session not found" in res_3000
        or "401" in res_3000
    ):
        print("[*] Port 3000 falló. Intentando Port 3002...")
        cmd2 = f'curl -s -X POST "http://127.0.0.1:3002/api/sendText" -H "accept: application/json" -H "X-Api-Key: {waha_key}" -H "Content-Type: application/json" -d "@/tmp/wa_payload.json"'
        stdin, stdout, stderr = ssh.exec_command(cmd2)
        res_3002 = stdout.read().decode("utf-8")
        print("Respuesta 3002:", res_3002)

except Exception as e:
    print(f"ERROR: {e}")
finally:
    ssh.close()
