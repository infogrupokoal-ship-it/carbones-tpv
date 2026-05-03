@echo off
title Despliegue Zero-Touch a Kamatera VPS
color 0B

echo ====================================================
echo =     DESPLIEGUE ZERO-TOUCH A KAMATERA VPS         =
echo ====================================================
echo.

echo [1/3] Sincronizando repositorio local con GitHub (main)...
git add .
git commit -m "Auto-deploy a Kamatera VPS: Actualizacion de assets y optimizacion frontend"
git push origin main
if %ERRORLEVEL% NEQ 0 (
    echo [X] Error al subir los cambios a GitHub. Revisa la conexion o conflictos.
    pause
    exit /b 1
)

echo.
echo [2/3] Conectando a Kamatera VPS (113.30.148.104) por SSH...
echo.
echo NOTA: Se solicitara la contrasena del usuario 'root'. 
echo Contrasena actual: 633660438gK1234
echo.

:: Utilizamos SSH para ejecutar una cadena de comandos en el VPS:
:: 1. Ir a la carpeta correcta (/opt/carbones_tpv)
:: 2. Actualizar desde Git
:: 3. Activar entorno virtual
:: 4. Instalar dependencias nuevas si las hay
:: 5. Reiniciar el servicio systemd (tpv.service)
ssh root@113.30.148.104 "cd /opt/carbones_tpv && git pull origin main && source venv/bin/activate && pip install -r requirements.txt && systemctl restart tpv.service"

if %ERRORLEVEL% NEQ 0 (
    echo [X] Error durante la ejecucion remota por SSH.
    pause
    exit /b 1
)

echo.
echo [3/3] Despliegue completado con exito. El servidor remoto se ha reiniciado.
echo Verifica el estado en: http://113.30.148.104:5001
echo.
pause
