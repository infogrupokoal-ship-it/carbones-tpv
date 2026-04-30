#!/bin/bash
# --- SCRIPT DE ARRANQUE PROFESIONAL TPV CARBONES Y POLLOS ---

echo "🚀 Iniciando Ecosistema TPV Carbones y Pollos..."

# 1. Asegurar Wake Lock para que Android no mate el proceso
termux-wake-lock

# 2. Navegar al directorio y actualizar código (opcional)
cd ~/carbones-tpv
# git pull origin master

# 3. Comprobar dependencias
pip install -r requirements.txt --quiet

# 4. Iniciar el puente de hardware en segundo plano
echo "🔌 Conectando puente de hardware (Impresoras)..."
nohup python local_printer_bridge.py > bridge.log 2>&1 &

# 5. Iniciar el servidor backend principal
echo "🔥 Arrancando Servidor de Producción..."
# Usamos uvicorn directamente para simplicidad en Termux
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
