@echo off
set "BACKUP_SCRIPT=d:\proyecto\carbones_y_pollos_tpv\scripts\automated_backup.py"
set "WATCHDOG_SCRIPT=d:\proyecto\carbones_y_pollos_tpv\watchdog_bridge.bat"
set "PYTHON_EXE=python"

echo [GRUPO KOAL] Configurando tareas programadas industriales...

:: 1. Tarea de Backup cada 4 horas
schtasks /create /tn "Koal_TPV_Backup" /tr "%PYTHON_EXE% %BACKUP_SCRIPT%" /sc hourly /mo 4 /f
if %ERRORLEVEL% EQU 0 (
    echo [+] Tarea de Backup creada: Se ejecutara cada 4 horas.
) else (
    echo [!] Error al crear tarea de Backup.
)

:: 2. Tarea de Watchdog al inicio del sistema
schtasks /create /tn "Koal_TPV_Watchdog" /tr "%WATCHDOG_SCRIPT%" /sc onstart /ru SYSTEM /f
if %ERRORLEVEL% EQU 0 (
    echo [+] Tarea de Watchdog creada: Se ejecutara al arrancar el sistema.
) else (
    echo [!] Error al crear tarea de Watchdog.
)

echo.
echo [CONFIGURACION COMPLETADA] El sistema ahora es autonomo.
pause
