#!/data/data/com.termux/files/usr/bin/bash
echo "Iniciando copia de seguridad de la base de datos de Carbones y Pollos..."
FECHA=$(date +"%Y%m%d_%H%M%S")
cp tpv_data.sqlite backups_db/tpv_data_${FECHA}.sqlite.bak 2>/dev/null || (mkdir -p backups_db && cp tpv_data.sqlite backups_db/tpv_data_${FECHA}.sqlite.bak)
echo "✅ Backup completado: backups_db/tpv_data_${FECHA}.sqlite.bak"
