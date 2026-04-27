import requests

WAHA_URL = "http://113.30.148.104:3000/api/sendText"
API_KEY = "1060705b0a574d1fbc92fa10a2b5aca7"
PHONE = "34604864187"

mensaje = """Hola Fran, soy el Agente de IA. 🚀
He completado toda la infraestructura del proyecto **Carbones y Pollos TPV**. 

Para mañana, esto es lo que debes tener en cuenta y lo que puedes decirme para ejecutar los despliegues finales y pruebas:

1️⃣ *Lógica de Turnos Completada*: El inventario ya diferencia entre 'Sobrantes de ayer', 'Prod. Mañana', 'Prod. Tarde', y 'Mermas'. Todo se refleja visualmente en el Dashboard con botones de acción rápida, sin necesidad de comandos raros.
2️⃣ *Cierre Z Inteligente*: El reporte_z ahora no solo saca la caja, sino que escanea el inventario y calcula los sobrantes exactos listos para el día siguiente.
3️⃣ *Arquitectura Cloud-Edge Validada*: El botón de abrir caja de forma remota funciona. Todo el código del puente está listo y documentado.

*PRÓXIMOS PASOS (Lo que me tienes que pedir mañana):*
👉 "Sube el proyecto a Render. Ya he creado el repo de GitHub carbones-y-pollos-tpv y lo he enlazado."
👉 "Haz una prueba de extremo a extremo: marca una venta en efectivo desde el móvil y comprueba que se registra en el Cierre Z y actualiza el inventario."
👉 "Verifica que el demonio de sincronización (tablet) se levanta automáticamente al iniciar Windows."

¡El proyecto está casi a punto de caramelo! 🍗🔥
"""

payload = {
    "chatId": f"{PHONE}@c.us",
    "text": mensaje,
    "session": "default"
}

headers = {
    "Content-Type": "application/json",
    "X-Api-Key": API_KEY
}

try:
    print("Enviando reporte a WAHA...")
    response = requests.post(WAHA_URL, json=payload, headers=headers, timeout=15)
    print("Estado HTTP:", response.status_code)
    print("Respuesta:", response.text)
except Exception as e:
    print("Error enviando:", e)
