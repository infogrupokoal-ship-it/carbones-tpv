#!/data/data/com.termux/files/usr/bin/bash

# ====================================================
# INSTALADOR MÁGICO TPV ANDROID (Vía HTTP LAN)
# ====================================================
echo "===================================================="
echo "Iniciando instalación profesional de la TPV Carbones..."
echo "Descargando código fuente desde Windows..."

PC_IP="192.168.1.237"
PORT="8000"
BASE_URL="http://$PC_IP:$PORT"

# Crear estructura
mkdir -p ~/carbones_y_pollos_tpv/static
mkdir -p ~/.termux/boot
mkdir -p ~/.shortcuts
cd ~/carbones_y_pollos_tpv

# Lista de archivos a descargar
FILES=(
    "main.py"
    "models.py"
    "arrancar_tpv.sh"
    "soporte_remoto.sh"
    "static/index.html"
    "static/start.html"
    "requirements_tpv.txt"
)

# Descargar cada archivo
for FILE in "${FILES[@]}"; do
    echo " -> Descargando $FILE..."
    curl -s -O --create-dirs --output-dir $(dirname $FILE) "$BASE_URL/$FILE"
done

echo "===================================================="
echo "Configurando entorno y dependencias (Esto puede tardar unos minutos)..."

# Instalar dependencias base de Termux si faltan
pkg install -y python rust binutils libssl-dev libffi-dev || true

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    python -m venv venv
fi

# Activar entorno e instalar librerías de Python
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements_tpv.txt

# Configurar Auto-Arranque de TODO (Termux:Boot)
echo "#!/data/data/com.termux/files/usr/bin/bash" > ~/.termux/boot/01-sshd.sh
echo "termux-wake-lock" >> ~/.termux/boot/01-sshd.sh
echo "sshd" >> ~/.termux/boot/01-sshd.sh
echo "cd ~/carbones_y_pollos_tpv" >> ~/.termux/boot/01-sshd.sh
echo "nohup ./arrancar_tpv.sh > boot_tpv.log 2>&1 &" >> ~/.termux/boot/01-sshd.sh
chmod +x ~/.termux/boot/01-sshd.sh

# Configurar Botón de 1-Clic (Termux:Widget)
echo "#!/data/data/com.termux/files/usr/bin/bash" > ~/.shortcuts/INICIAR_TPV.sh
echo "cd ~/carbones_y_pollos_tpv" >> ~/.shortcuts/INICIAR_TPV.sh
echo "./arrancar_tpv.sh" >> ~/.shortcuts/INICIAR_TPV.sh
chmod +x ~/.shortcuts/INICIAR_TPV.sh

chmod +x *.sh

echo "===================================================="
echo "¡INSTALACIÓN COMPLETADA CON ÉXITO!"
echo "Tu TPV ya tiene la última versión y está lista para trabajar."
echo "Para arrancar el motor ahora mismo, ejecuta:"
echo "./arrancar_tpv.sh"
echo "===================================================="
