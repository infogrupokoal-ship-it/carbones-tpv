#!/bin/bash

# 🚀 SCRIPT DE CONFIGURACIÓN MAESTRA DEL SERVIDOR - CARBONES Y POLLOS TPV
# Diseñado para Ubuntu/Debian en entornos VPS/Cloud

set -e

# Colores para la consola
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}=== Iniciando Despliegue Profesional TPV v2.6 ===${NC}"

# 1. Actualización de Sistema
echo -e "${GREEN}[1/6] Actualizando paquetes del sistema...${NC}"
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv nginx git curl sqlite3

# 2. Configuración de Directorios y Permisos
echo -e "${GREEN}[2/6] Estructurando directorios de aplicación...${NC}"
APP_DIR="/opt/carbones_tpv"
LOG_DIR="/var/log/tpv"

sudo mkdir -p $APP_DIR
sudo mkdir -p $LOG_DIR
sudo chown -R $USER:$USER $APP_DIR
sudo chown -R www-data:www-data $LOG_DIR

# 3. Entorno Virtual y Dependencias
echo -e "${GREEN}[3/6] Creando entorno virtual Python...${NC}"
cd $APP_DIR
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 4. Configuración de Nginx como Reverse Proxy
echo -e "${GREEN}[4/6] Configurando Nginx...${NC}"
cat <<EOF | sudo tee /etc/nginx/sites-available/tpv
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static {
        alias $APP_DIR/static;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/tpv /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl restart nginx

# 5. Instalación del Servicio Systemd
echo -e "${GREEN}[5/6] Instalando servicio de fondo (Systemd)...${NC}"
sudo cp scripts/tpv.service /etc/systemd/system/tpv.service
sudo systemctl daemon-reload
sudo systemctl enable tpv

# 6. Finalización
echo -e "${BLUE}===============================================${NC}"
echo -e "${GREEN}✅ SERVIDOR CONFIGURADO CON ÉXITO${NC}"
echo -e "Acceso API: http://localhost:8000"
echo -e "Logs: $LOG_DIR/server.log"
echo -e "Ejecuta 'sudo systemctl start tpv' para iniciar."
echo -e "${BLUE}===============================================${NC}"
