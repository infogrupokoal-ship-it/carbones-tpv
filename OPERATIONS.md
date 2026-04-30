# 📑 Manual de Operaciones Enterprise - Carbones y Pollos TPV

Este documento detalla los procedimientos operativos estándar (SOP) para el mantenimiento y resolución de incidencias del ecosistema TPV.

---

## 🛠️ Procedimientos Técnicos

### 1. Gestión de Servicios (VPS)
El sistema utiliza **Systemd** y **Docker Compose** para la orquestación.
- **Ver Estado:** `sudo systemctl status tpv` o `docker-compose ps`
- **Ver Logs en Tiempo Real:** `tail -f /var/log/tpv/server.log`
- **Reiniciar Sistema:** `scripts/deploy_vps.sh`

### 2. Recuperación ante Desastres (DRP)
En caso de corrupción de base de datos o fallo de hardware:
1. Localiza el último backup en `/opt/carbones_tpv/backups/`.
2. Detén el servicio: `docker-compose down`.
3. Restaura el archivo: `cp backups/tpv_enterprise_backup_YYYYMMDD.tar.gz ./ && tar -xzf ...`.
4. Levanta el sistema: `scripts/deploy_vps.sh`.

---

## 💰 Gestión Financiera

### 1. El Cierre Z
- **Automático:** Se ejecuta cada día a las **03:00 AM**. No requiere intervención.
- **Manual (Emergencia):** Accede al Panel de Admin -> Gestión -> Ejecutar Cierre Z. Se recomienda realizarlo si el local cierra antes de tiempo por festivo.

### 2. Arqueo de Caja
El sistema solicita un **Arqueo Ciego**. El cajero debe contar el efectivo físico e introducirlo. El sistema calculará la diferencia contra el total teórico y generará un log de advertencia si la diferencia supera los 5€.

---

## 🤖 Inteligencia Artificial (Koal-AI)
- Si Koal-AI no responde, verifica que la `GOOGLE_API_KEY` en el `.env` sea válida.
- Puedes consultar a la IA sobre: "Nivel de producción sugerido para mañana", "Análisis de ventas del fin de semana" o "Estado crítico de stock".

---

## 📞 Escalado de Incidencias
1. **Nivel 1 (Operativo):** Cajero/Encargado. (Problemas de ticket, apertura de cajón).
2. **Nivel 2 (Técnico Local):** Administrador de Sistemas. (Fallo de red, reinicio de servicios).
3. **Nivel 3 (Desarrollo):** Soporte Koal. (Bugs de software, errores de IA).
