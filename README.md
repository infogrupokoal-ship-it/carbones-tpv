# 🍗 Carbones y Pollos TPV - Enterprise Ecosystem v2.6

SISTEMA INTEGRAL DE GESTIÓN GASTRONÓMICA IMPULSADO POR IA

---

## 🏗️ Arquitectura del Ecosistema
El sistema se basa en una arquitectura de **Capa de Servicios Modular** (Service Layer) con persistencia desacoplada y soporte nativo para **Edge Computing** (Offline-First).

1.  **Backend (FastAPI):** Núcleo de alta disponibilidad con middleware de telemetría y seguridad.
2.  **Koal-AI (Gemini 1.5):** Inteligencia operacional que analiza ventas y sugiere niveles de producción.
3.  **Enterprise Hub:** Punto de acceso centralizado con diseño Glassmorphism para todas las terminales.
4.  **Sync Daemon:** Servicio de fondo que garantiza la sincronización entre el local físico y la nube.
5.  **Audit Engine:** Generación automática de Reportes Z y arqueos ciegos contables.

---

## 🚀 Despliegue en Producción (VPS / Linux)

### 1. Preparación del Entorno
```bash
sudo apt update && sudo apt install python3-venv git -y
git clone https://github.com/tu-usuario/carbones-tpv.git /opt/carbones_tpv
cd /opt/carbones_tpv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configuración de Servicios (Systemd)
El sistema incluye un archivo `scripts/tpv.service` pre-configurado.
```bash
sudo cp scripts/tpv.service /etc/systemd/system/tpv.service
sudo systemctl daemon-reload
sudo systemctl enable tpv
sudo systemctl start tpv
```

---

## 🛠️ Herramientas Administrativas (CLI)
Para monitorizar el servidor sin interfaz gráfica, utiliza las herramientas incluidas en `scripts/`:

*   **Monitor de Sistema:** `python scripts/admin_cli.py` (Ventas y salud en tiempo real).
*   **Smoke Test:** `python scripts/smoke_test.py` (Verificación de integridad de red).
*   **Gestor de Backups:** `python scripts/backup_manager.py` (Copia de seguridad instantánea).

---

## 🔒 Seguridad y Auditoría
*   **Logs:** Ubicados en `instance/logs/`. El sistema rota logs automáticamente.
*   **Cierre Z:** Los cierres se ejecutan diariamente a las 03:00 AM (configurado en `scheduler.py`).
*   **Persistencia:** En entornos cloud, asegúrate de montar un volumen en `/data` para que `tpv_data.sqlite` sea persistente.

---

## 📧 Contacto y Soporte
Desarrollado por **Antigravity AI Team** para **Grupo Koal - Advanced Agentic Coding**.
v2.6 - Build 2026.04.30
