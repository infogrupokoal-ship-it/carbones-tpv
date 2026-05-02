# 🛡️ Carbones y Pollos TPV - Manual de Operaciones Enterprise

Este documento establece los protocolos de operación, mantenimiento y arquitectura del ecosistema TPV v3.1.

## 🏗️ Arquitectura del Sistema

El sistema utiliza un patrón **Edge-Cloud Hybrid**:

- **Backend:** FastAPI (Python 3.10+) con arquitectura asíncrona.

- **Base de Datos:** SQLite (Local/Edge) con sincronización bidireccional mediante demonios persistentes.

- **Hardware Bridge:** Puente de periféricos (ESC/POS) mediante colas asíncronas.

- **Frontend:** Single Page Application (SPA) con diseño Glassmorphism y capacidades PWA.

## 🚀 Protocolo de Despliegue

### Requisitos del Servidor (VPS)

- Ubuntu 22.04 LTS o superior.

- Docker & Docker Compose (v2.0+).

- Puertos abiertos: 22 (SSH), 80 (HTTP), 443 (HTTPS), 8000 (API - Opcional).

### Pasos de Instalación

1. Clonar repositorio: `git clone https://github.com/infogrupokoal-ship-it/carbones-tpv.git`

2. Configurar entorno: `cp .env.example .env` (Ajustar claves de API).

3. Ejecutar script maestro: `sudo bash scripts/setup_server.sh`.

## 📊 Monitorización y Telemetría

- **Logs Operativos:** Accesibles vía `/api/system/logs` o en el panel de administración.

- **Salud del Sistema:** Endpoint `/health` para monitorización de hardware (CPU/RAM/Disco).

- **Persistencia:** Logs locales almacenados en `instance/server.log` con rotación diaria.

## 🛠️ Mantenimiento y Backup

- **Backups:** Automatizados vía `scripts/backup_manager.py` (Snapshots diarios).

- **Actualizaciones:** Push a `main` desencadena despliegue automático en Render y actualización manual en VPS vía `git pull`.

## 🛡️ Seguridad Industrial

- **Rate Limiting:** Protegido contra ataques de fuerza bruta.

- **Headers:** HSTS, X-Frame-Options (DENY), CSP (Content Security Policy) activados.

- **Data Integrity:** Cierre Z con arqueo ciego obligatorio para evitar desviaciones.

---
© 2026 Grupo Koal - Carbones y Pollos. Documentación Confidencial.
