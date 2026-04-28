@echo off
title Instalador 1-Clic TPV Android (Auto-Descubrimiento)
color 0B
echo ====================================================
echo =     INSTALADOR MAESTRO TPV ANDROID (OFFLINE)     =
echo ====================================================
echo.
echo Buscando automaticamente la tablet TPV en la red local...
echo Por favor, asegurate de que la tablet tiene la app Termux abierta.
echo.
python auto_deploy.py
echo.
pause
