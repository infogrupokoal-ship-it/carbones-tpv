#!/data/data/com.termux/files/usr/bin/bash
# Script para levantar una "puerta trasera" temporal desde Termux

echo "==========================================="
echo "   SOPORTE REMOTO - CARBONES Y POLLOS      "
echo "==========================================="
echo "Iniciando servidor SSH local (puerta abierta de consola)..."
sshd
echo "Levantando túnel remoto..."
echo "Te aparecerá una dirección web para el TPV y un puerto para SSH."
echo "Para cerrar la puerta, cierra esta ventana."
echo "==========================================="

# El túnel de localhost.run es gratis, apunta al puerto de nuestro TPV y al SSH
# StrictHostKeyChecking=no evita que la tablet pregunte yes/no la primera vez
ssh -R 80:localhost:5001 -R 22:localhost:8022 -o StrictHostKeyChecking=no nokey@localhost.run
