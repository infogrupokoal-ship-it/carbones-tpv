#!/data/data/com.termux/files/usr/bin/bash
# Script para iniciar la TPV en Android desde Termux:Widget

echo "Encendiendo el motor de la TPV..."

# Intentamos ir al directorio del proyecto
cd ~/storage/downloads/carbones_y_pollos_tpv 2>/dev/null || cd ~/carbones_y_pollos_tpv 2>/dev/null || cd /sdcard/Download/carbones_y_pollos_tpv 2>/dev/null || cd "$PWD"

# Si existe un entorno virtual, lo activamos
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Matar instancia anterior si la hubiera
pkill -f "python main.py"
pkill -f "uvicorn"

# Levantar el backend de FastAPI silenciosamente en el puerto 5001
nohup python main.py > tpv_motor.log 2>&1 &

echo "Motor encendido."
sleep 4

echo "Abriendo la interfaz visual en Google Chrome..."
# Forzar a Android a abrir Chrome apuntando a nuestro motor local
am start -a android.intent.action.VIEW -d "http://127.0.0.1:5001" -n com.android.chrome/com.google.android.apps.chrome.Main

echo "¡Listo! Ya puedes trabajar. Mantén Termux abierto en segundo plano."
