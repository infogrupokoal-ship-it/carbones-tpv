# 🐔 Carbones y Pollos - Enterprise TPV Ecosystem v2.0

Este documento proporciona una visión técnica de alto nivel del ecosistema **Carbones y Pollos**, un sistema TPV (Punto de Venta) de alto rendimiento diseñado para la operativa 24/7 en asadores artesanales.

## 🏗️ Arquitectura del Sistema

El ecosistema sigue un modelo de **Edge Computing con Sincronización Cloud**:

1. **Core (Backend)**: Desarrollado en **FastAPI**, modularizado para separar lógica de ventas, inventario, RRHH y administración. Utiliza **SQLAlchemy** con el patrón Repository para una persistencia robusta.

2. **Hardware Bridge**: Un componente local (`local_printer_bridge.py`) que gestiona la comunicación directa con impresoras térmicas (USB/Network) y balanzas, independizando la operativa física de la estabilidad de internet.

3. **Frontend Glassmorphism**: Una interfaz moderna y reactiva diseñada con **Tailwind CSS**, centrada en la eficiencia táctil y la claridad visual bajo estrés operativo.

4. **AI Intelligence**: Integración con **Google Gemini** para análisis de ventas, gestión de inventario predictivo y asistente virtual omnicanal (WhatsApp + Dashboard).

## 📦 Módulos Principales

### 🛒 TPV Kiosko

Interfaz de ventas optimizada para tablets. Gestión de categorías, stock en tiempo real y flujos de pago integrados.

* **Tecnología**: HTML5/JS Vanilla + Design System CSS.

* **Offline-First**: Funciona sin internet gracias al Service Worker avanzado.

### 🔥 Kitchen Display System (KDS)

Monitor de cocina que elimina el papel.

* **Alertas**: Alarma roja visual para pedidos con más de 15 min de espera.

* **Sync**: Actualización bidireccional inmediata con la caja.

### 📊 Business Intelligence (BI)

Cuadro de mando ejecutivo para gerencia.

* **Métricas**: Gráficos dinámicos de ventas, mermas y rendimiento de personal.

* **AI Insights**: Sugerencias automáticas basadas en tendencias de venta.

### 👥 RRHH & Telemetría

* **Fichajes**: Control de presencia mediante PIN.

* **Status**: Monitoreo de salud del bridge local y estado de los backups.

## 🚀 Despliegue y Mantenimiento

* **Docker Ready**: El proyecto incluye `Dockerfile` y `docker-compose.yml` para un despliegue instantáneo en cualquier VPS o servidor local.

* **Autonomía**: Tareas programadas (`scheduler.py`) realizan backups diarios y cierres de caja (Z) de forma desatendida.

* **PWA**: Instalable en Android/iOS con comportamiento de aplicación nativa.

---

**Desarrollado con rigor técnico para maximizar la rentabilidad y eficiencia operativa.**
