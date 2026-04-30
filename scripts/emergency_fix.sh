#!/bin/bash

# 🚨 SCRIPT DE RECUPERACIÓN DE EMERGENCIA - CARBONES Y POLLOS TPV
# Diseñado para diagnosticar y reparar fallos comunes de despliegue.

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${RED}=== Iniciando Protocolo de Emergencia ===${NC}"

# 1. Verificar directorios críticos
echo -e "[*] Verificando estructura de directorios..."
mkdir -p instance static logs
chmod -R 755 instance static logs

# 2. Limpiar cachés corruptos
echo -e "[*] Purgando cachés de Python..."
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# 3. Validar base de datos
if [ -f "tpv_data.sqlite" ]; then
    echo -e "[✅] Base de datos detectada."
else
    echo -e "[⚠️] Base de datos no encontrada. Se creará una nueva al iniciar."
fi

# 4. Verificar dependencias
echo -e "[*] Validando entorno virtual..."
if [ -d "venv" ]; then
    source venv/bin/activate
    pip install -r requirements.txt
else
    echo -e "${RED}[❌] Entorno venv no detectado. Reinstale con setup_server.sh${NC}"
fi

# 5. Reiniciar servicios
echo -e "[*] Reiniciando servicios del sistema..."
sudo systemctl daemon-reload
sudo systemctl restart tpv
sudo systemctl restart nginx

echo -e "${GREEN}=== SISTEMA RECUPERADO Y OPTIMIZADO ===${NC}"
echo -e "Estado del servicio: $(sudo systemctl is-active tpv)"
