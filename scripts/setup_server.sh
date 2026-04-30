#!/bin/bash

# ==============================================================================
# 🚀 SCRIPT DE CONFIGURACIÓN MAESTRA DEL SERVIDOR - CARBONES Y POLLOS TPV
# Diseñado para Ubuntu/Debian en entornos VPS/Cloud
# Versión: Enterprise 3.0
# ==============================================================================

set -e

# Colores para la consola
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}=== Iniciando Despliegue Profesional TPV v3.0 ===${NC}"

# 1. Actualización de Sistema y Seguridad (Firewall)
echo -e "${GREEN}[1/6] Actualizando paquetes y configurando Firewall (UFW)...${NC}"
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv nginx git curl sqlite3 ufw
# Configuración del Firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
# Habilitamos el firewall de manera no interactiva
echo "y" | sudo ufw enable

# 2. Configuración de Directorios y Permisos
echo -e "${GREEN}[2/6] Estructurando directorios de aplicación en /opt...${NC}"
APP_DIR="/opt/carbones_tpv"
LOG_DIR="/var/log/tpv"

sudo mkdir -p $APP_DIR
sudo mkdir -p $LOG_DIR
sudo chown -R $USER:$USER $APP_DIR
sudo chown -R www-data:www-data $LOG_DIR

# Copiar archivos actuales al directorio de producción si estamos ejecutando desde /root/
if [ "$PWD" != "$APP_DIR" ]; then
    echo -e "${GREEN}Copiando archivos al directorio de producción $APP_DIR...${NC}"
    sudo cp -r ./* $APP_DIR/
    sudo chown -R $USER:$USER $APP_DIR
fi

# 3. Entorno Virtual y Dependencias
echo -e "${GREEN}[3/6] Creando entorno virtual Python...${NC}"
cd $APP_DIR
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    pip install gunicorn uvicorn reportlab
fi

# 4. Configuración de Nginx como Reverse Proxy
echo -e "${GREEN}[4/6] Configurando Nginx para Alta Disponibilidad...${NC}"
cat <<EOF | sudo tee /etc/nginx/sites-available/tpv
server {
    listen 80;
    server_name _;

    # Compresión Gzip para mejorar rendimiento
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # Ocultar la versión de Nginx por seguridad
    server_tokens off;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Tiempos de espera ampliados
        proxy_connect_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Caché agresivo para archivos estáticos
    location /static/ {
        alias $APP_DIR/static/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
        access_log off;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/tpv /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl restart nginx

# 5. Instalación del Servicio Systemd
echo -e "${GREEN}[5/6] Instalando servicio Systemd (Gunicorn)...${NC}"
cat <<EOF | sudo tee /etc/systemd/system/tpv.service
[Unit]
Description=Carbones y Pollos TPV - Gunicorn Daemon
After=network.target

[Service]
User=$USER
Group=www-data
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
Environment="PYTHONPATH=$APP_DIR"
ExecStart=$APP_DIR/venv/bin/gunicorn --workers 3 --worker-class uvicorn.workers.UvicornWorker --bind 127.0.0.1:8000 backend.main:app

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable tpv
sudo systemctl restart tpv

# 6. Finalización
echo -e "${BLUE}========================================================================${NC}"
echo -e "${GREEN}✅ SERVIDOR CONFIGURADO CON ÉXITO Y SECURIZADO${NC}"
echo -e "Aplicación migrada a: $APP_DIR"
echo -e "Firewall UFW habilitado (Puertos 22, 80, 443 permitidos)"
echo -e "Nginx Reverse Proxy: Configurado"
echo -e "Servicio Systemd: 'tpv.service' activo"
echo -e "${BLUE}========================================================================${NC}"

