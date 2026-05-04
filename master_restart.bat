@echo off
title MASTER RESTART TPV
echo --- INICIANDO LIMPIEZA TOTAL ---
taskkill /f /im python.exe
timeout /t 2 /nobreak
del /f D:\proyecto\carbones_y_pollos_tpv\instance\*.pid
echo --- REINICIANDO SERVICIOS ---
start "KOAL TPV WATCHDOG" cmd /c watchdog_bridge.bat
set PYTHONPATH=.
start "KOAL TPV BACKEND" python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
echo --- SISTEMA REINICIADO ---
pause
