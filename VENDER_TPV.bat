@echo off
title TPV Carbones y Pollos - Sistema de Ventas
color 0E

echo ====================================================
echo =     SISTEMA TPV - CARBONES Y POLLOS              =
echo ====================================================
echo.
echo Iniciando el servidor local de la TPV...
echo.

cd /d "d:\proyecto\carbones_y_pollos_tpv"

:: Matar procesos anteriores por seguridad (si existen)
taskkill /F /IM python.exe /T 2>nul
taskkill /IM uvicorn.exe /F /T 2>nul

:: Iniciar la aplicacion de forma independiente en otra ventana
start "Servidor TPV (NO CERRAR)" cmd /c "title Motor TPV Backend & color 0B & python main.py"

echo Esperando a que el motor arranque...
timeout /t 4 /nobreak >nul

echo.
echo Abriendo la pantalla de ventas en tu navegador...
start http://127.0.0.1:5001

echo.
echo ====================================================
echo = TODO LISTO PARA VENDER.                          =
echo = Mantén la otra ventana negra minimizada.         =
echo ====================================================
echo.
pause
