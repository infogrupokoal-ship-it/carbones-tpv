import requests
import json

waha_key = '1060705b0a574d1fbc92fa10a2b5aca7'
url = "http://113.30.148.104:3000/api/sendText"

with open(r'd:\proyecto\carbones_y_pollos_tpv\PLAN_ESTRATEGICO.md', 'r', encoding='utf-8') as f:
    plan_text = f.read()

mensaje = "🤖 *Hola, soy tu IA de la TPV (Gemini).* 🤖\n\nAquí tienes el Plan Estratégico y las instrucciones para el local a prueba de cocineros, enviado desde el nodo de comunicaciones de Grupo Koal como pediste:\n\n" + plan_text

payload = {
    "session": "default",
    "chatId": "34604864187@c.us",
    "text": mensaje
}

headers = {
    "accept": "application/json",
    "X-Api-Key": waha_key,
    "Content-Type": "application/json"
}

try:
    response = requests.post(url, json=payload, headers=headers)
    print("Status 3000:", response.status_code)
    print("Response 3000:", response.text)
    
    if response.status_code != 201:
        url2 = "http://113.30.148.104:3002/api/sendText"
        response2 = requests.post(url2, json=payload, headers=headers)
        print("Status 3002:", response2.status_code)
        print("Response 3002:", response2.text)

except Exception as e:
    print(f"ERROR: {e}")
