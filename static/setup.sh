#!/bin/bash
# Carbones y Pollos TPV - Industrial Installer v4.5
# Compatible con Termux (Android) y Linux/macOS

set -e

echo "🚀 Iniciando Instalador Industrial TPV v4.5..."
echo "-------------------------------------------"

# 1. Detectar entorno
if [ -d "/data/data/com.termux/files/home" ]; then
    echo "📱 Entorno Termux detectado."
    pkg update -y
    pkg install -y git python python-pip openssh
else
    echo "💻 Entorno Desktop detectado."
fi

# 2. Clonar/Actualizar Repositorio
REPO_DIR="$HOME/carbones-tpv"
if [ -d "$REPO_DIR" ]; then
    echo "🔄 Actualizando repositorio existente..."
    cd "$REPO_DIR"
    git pull origin main
else
    echo "📥 Clonando repositorio..."
    git clone https://github.com/infogrupokoal-ship-it/carbones-tpv.git "$REPO_DIR"
    cd "$REPO_DIR"
fi

# 3. Preparar Entorno Python
echo "🐍 Instalando dependencias de Python..."
pip install --upgrade pip
pip install fastapi uvicorn requests python-dotenv psutil sqlalchemy pydantic slowapi

# 4. Configurar .env si no existe
if [ ! -f ".env" ]; then
    echo "📝 Generando archivo de configuración por defecto..."
    echo "VPS_URL=https://carbones-tpv.onrender.com" > .env
    echo "DATABASE_URL=sqlite:///./tpv_data.sqlite" >> .env
    echo "SYNC_INTERVAL=15" >> .env
fi

# 5. Crear scripts de arranque
echo "⚙️ Configurando auto-arranque..."
if [ -d "$HOME/.termux/boot" ]; then
    cat <<EOF > ~/.termux/boot/tpv-start.sh
termux-wake-lock
cd $REPO_DIR
git pull origin main
nohup python local_printer_bridge.py > bridge.log 2>&1 &
nohup python sync_daemon.py > sync.log 2>&1 &
EOF
    chmod +x ~/.termux/boot/tpv-start.sh
    echo "✅ Auto-arranque configurado para Termux."
fi

echo "-------------------------------------------"
echo "✅ INSTALACIÓN COMPLETADA CON ÉXITO."
echo "Para arrancar manualmente:"
echo "cd $REPO_DIR"
echo "python local_printer_bridge.py &"
echo "python sync_daemon.py &"
echo "-------------------------------------------"
