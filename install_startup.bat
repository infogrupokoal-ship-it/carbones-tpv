@echo off
set "SCRIPT_PATH=d:\proyecto\carbones_y_pollos_tpv\scripts\launch_bridge_hidden.vbs"
set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"

echo [INSTALADOR GRUPO KOAL] Configurando inicio automatico...

if exist "%SCRIPT_PATH%" (
    copy /Y "%SCRIPT_PATH%" "%STARTUP_FOLDER%\KoalBridge.vbs"
    echo [+] Exito: El puente se ejecutara automaticamente al iniciar sesion.
) else (
    echo [!] ERROR: No se encontro el archivo %SCRIPT_PATH%
)

pause
