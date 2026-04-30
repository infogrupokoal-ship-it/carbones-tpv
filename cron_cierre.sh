#!/bin/bash
# Script para ejecutar el Cierre Z Automático en Linux/Termux
echo "[$(date)] Iniciando Cierre Z automatico..."
curl -X POST "http://localhost:8000/api/admin/trigger_cierre_z" -H "Content-Type: application/json" -d "{}"
echo ""
echo "[$(date)] Cierre Z finalizado."
