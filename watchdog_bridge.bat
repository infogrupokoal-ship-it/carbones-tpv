@echo off
title KOAL TPV WATCHDOG
echo [%DATE% %TIME%] Iniciando Watchdog de Puente de Hardware...
:loop
python "d:\proyecto\carbones_y_pollos_tpv\scripts\watchdog_bridge.py"
echo [%DATE% %TIME%] El puente se ha detenido. Reiniciando en 5 segundos...
timeout /t 5
goto loop
