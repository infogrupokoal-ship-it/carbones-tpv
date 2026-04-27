@echo off
title Puerta Abierta - TPV Remoto (Ngrok)
color 0A

echo ====================================================
echo =     PUERTA ABIERTA TPV - ACCESO DESDE CASA       =
echo ====================================================
echo.
echo Este script abrira una conexion segura para que puedas
echo domotizar y controlar la TPV (Windows) desde tu casa.
echo.
echo NOTA: Para que esto funcione, este PC (TPV) debe tener:
echo 1. Ngrok instalado y autenticado (ngrok config add-authtoken ...)
echo 2. Escritorio Remoto (RDP) habilitado en la configuracion de Windows.
echo 3. Un usuario de Windows CON CONTRASENA.
echo.
echo Presiona cualquier tecla para iniciar el tunel...
pause >nul

echo Iniciando tunel RDP (Escritorio Remoto)...
ngrok tcp 3389

echo.
echo Si el comando anterior fallo, asegurate de tener ngrok en tu PATH o en esta carpeta.
pause
