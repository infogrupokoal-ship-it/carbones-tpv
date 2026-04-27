#!/data/data/com.termux/files/usr/bin/bash
# INSTALADOR DE WIDGETS Y ACCESOS DIRECTOS PARA TERMUX

echo "================================================="
echo " CONFIGURANDO TPV EN TU ANDROID PARA 1 CLIC"
echo "================================================="

# 1. Asegurar que tenemos acceso a la memoria interna
termux-setup-storage
sleep 2

# 2. Crear la carpeta especial para los Widgets
mkdir -p ~/.shortcuts

# 3. Copiar los scripts de la TPV a la carpeta de Widgets
cp arrancar_tpv.sh ~/.shortcuts/Arrancar_TPV.sh
cp soporte_remoto.sh ~/.shortcuts/Soporte_Remoto.sh

# 4. Dar permisos de ejecución
chmod +x ~/.shortcuts/*.sh

echo "================================================="
echo "¡INSTALACIÓN COMPLETADA CON ÉXITO!"
echo "Ahora sal a tu pantalla de inicio de la Tablet,"
echo "Añade un Widget, busca 'Termux:Widget' y elige"
echo "'Arrancar_TPV'."
echo "================================================="
