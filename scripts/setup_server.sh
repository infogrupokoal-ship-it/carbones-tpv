#!/bin/bash

# 🚀 SCRIPT DE CONFIGURACIÓN MAESTRA DEL SERVIDOR - CARBONES Y POLLOS TPV ENTERPRISE v2.0
# Diseñado para Ubuntu/Debian en entornos VPS/Cloud de Alta Disponibilidad

set -e

# Colores para la consola
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}=== Iniciando Despliegue Profesional TPV Enterprise v2.0 ===${NC}"

# 1. Actualización de Sistema y Dependencias
echo -e "${GREEN}[1/8] Instalando dependencias Enterprise...${NC}"
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv nginx git curl sqlite3 ufw certbot python3-certbot-nginx logrotate

# 2. Configuración de Directorios y Permisos
echo -e "${GREEN}[2/8] Estructurando directorios de aplicación...${NC}"
APP_DIR="/opt/carbones_tpv"
LOG_DIR="/var/log/tpv"

sudo mkdir -p $APP_DIR
sudo mkdir -p $LOG_DIR
sudo chown -R $USER:$USER $APP_DIR
sudo chown -R www-data:www-data $LOG_DIR

# 3. Entorno Virtual
echo -e "${GREEN}[3/8] Entorno virtual Python...${NC}"
cd $APP_DIR
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
# Instalación de SlowApi para Rate Limiting
pip install slowapi

# 4. Hardening de Firewall (UFW)
echo -e "${GREEN}[4/8] Blindando puertos con UFW...${NC}"
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
# Forzar recarga (No bloquea la sesión activa actual normalmente)
sudo ufw --force enable

# 5. Configuración Avanzada de Nginx
echo -e "${GREEN}[5/8] Configurando Nginx de alto rendimiento...${NC}"
cat <<EOF | sudo tee /etc/nginx/sites-available/tpv
proxy_cache_path /tmp/nginx_cache levels=1:2 keys_zone=my_cache:10m max_size=1g inactive=60m use_temp_path=off;

server {
    listen 80;
    server_name _; # Se actualizará por certbot si hay dominio

    # Gzip Compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private auth;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml application/javascript;

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline' 'unsafe-eval'" always;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Timeout settings for slow clients/AI requests
        proxy_read_timeout 90s;
        proxy_connect_timeout 90s;
    }

    location /static/ {
        alias $APP_DIR/static/;
        expires 365d;
        add_header Cache-Control "public, no-transform";
        access_log off;
    }

    # Bloquear acceso a archivos sensibles
    location ~ /\. {
        deny all;
    }
    location = /tpv_data.sqlite {
        deny all;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/tpv /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl restart nginx

# 6. Rotación de Logs (Logrotate)
echo -e "${GREEN}[6/8] Configurando Logrotate para telemetría...${NC}"
cat <<EOF | sudo tee /etc/logrotate.d/tpv-enterprise
/var/log/tpv/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl restart tpv.service > /dev/null
    endscript
}
EOF

# 7. Instalación de Servicios Systemd
echo -e "${GREEN}[7/8] Orquestando microservicios Systemd...${NC}"
sudo cp scripts/tpv.service /etc/systemd/system/
sudo cp scripts/tpv-sync.service /etc/systemd/system/
sudo cp scripts/tpv-hardware.service /etc/systemd/system/
sudo cp scripts/tpv-maintenance.service /etc/systemd/system/
sudo cp scripts/tpv-maintenance.timer /etc/systemd/system/

sudo systemctl daemon-reload

sudo systemctl enable tpv
sudo systemctl enable tpv-sync
sudo systemctl enable tpv-hardware
sudo systemctl enable tpv-maintenance.timer

# 8. Finalización
echo -e "${BLUE}===============================================${NC}"
echo -e "${GREEN}✅ INFRAESTRUCTURA ENTERPRISE CONFIGURADA${NC}"
echo -e "Servicios listos para arrancar:"
echo -e "  sudo systemctl start tpv"
echo -e "  sudo systemctl start tpv-sync"
echo -e "  sudo systemctl start tpv-hardware"
echo -e "  sudo systemctl start tpv-maintenance.timer"
echo -e ""
echo -e "Para activar HTTPS (Si tienes un dominio apuntando aquí):"
echo -e "  sudo certbot --nginx -d tu-dominio.com"
echo -e "${BLUE}===============================================${NC}"
