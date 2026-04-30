@echo off
REM Script para ejecutar el Cierre Z Automático en Windows
echo [%date% %time%] Iniciando Cierre Z automatico...
curl -X POST "http://localhost:8000/api/admin/trigger_cierre_z" -H "Content-Type: application/json" -d "{}"
echo.
echo [%date% %time%] Cierre Z finalizado.
