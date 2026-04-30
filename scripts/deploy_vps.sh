#!/bin/bash

# Script de Despliegue Automatizado para VPS (Ubuntu/Debian)
# Carbones y Pollos TPV - Enterprise v2.5

echo "🚀 Iniciando despliegue en VPS..."

# 1. Actualizar repositorio
git pull origin main

# 2. Instalar dependencias
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt

# 3. Configurar Permisos
chmod -R 755 static
mkdir -p backend/logs
chmod 777 backend/logs

# 4. Configurar Systemd (Si no existe)
if [ ! -f "/etc/systemd/system/tpv.service" ]; then
    echo "⚙️ Configurando servicio Systemd..."
    sudo cp scripts/tpv.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable tpv
fi

# 5. Reiniciar Servicio
sudo systemctl restart tpv

echo "✅ Despliegue completado con éxito."
echo "🔗 URL: http://$(curl -s ifconfig.me):8000"
