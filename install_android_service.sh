#!/bin/bash
# INSTALADOR DE AUTO-ARRANQUE PARA TPV ANDROID (Termux:Boot)
# Este script configura la tablet para que "local_printer_bridge.py" 
# arranque solo al encender la pantalla, sin que los cocineros toquen nada.

echo "================================================="
echo " CONFIGURANDO AUTO-ARRANQUE DE IMPRESORA TPV "
echo "================================================="

# 1. Asegurar que existe el directorio de arranque de Termux
mkdir -p ~/.termux/boot/

# 2. Crear el archivo de arranque maestro
cat << 'EOF' > ~/.termux/boot/arranque_tpv.sh
#!/bin/bash

# Bloquear la CPU para que Android no duerma el proceso de la impresora
termux-wake-lock

# Iniciar el puente de la impresora en segundo plano
# Busca la carpeta de carbones_y_pollos_tpv en descargas (ajustar si está en otro lado)
cd /storage/emulated/0/Download/carbones_y_pollos_tpv || cd ~/carbones-tpv

# Ejecutar silenciosamente y guardar los logs
nohup python local_printer_bridge.py > ~/.termux/boot/impresora_log.txt 2>&1 &
EOF

# 3. Darle permisos de ejecución para que el sistema pueda lanzarlo
chmod +x ~/.termux/boot/arranque_tpv.sh

echo ""
echo "✅ Instalación completada con éxito."
echo ""
echo "⚠️ PASO FINAL OBLIGATORIO:"
echo "1. Debes descargar la app 'Termux:Boot' desde F-Droid o Google Play."
echo "2. Ábrela UNA VEZ y concédele todos los permisos que pida (inicio automático)."
echo "3. ¡Listo! Reinicia la tablet para probar. El cajón y la impresora ya funcionarán solos."
echo "================================================="
