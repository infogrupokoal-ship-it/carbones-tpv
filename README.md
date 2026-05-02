# 🍗 Carbones y Pollos TPV Enterprise v4.4

## 🚀 Ecosistema de Gestión Retail Inteligente

Sistema integral de Punto de Venta (TPV), Gestión de Cocina (KDS) e Inteligencia de Negocio (BI) diseñado para la máxima eficiencia operativa en entornos de hostelería de alto rendimiento.

### 🏗️ Arquitectura del Sistema

* **Backend Industrial**: Basado en FastAPI + SQLAlchemy (SQLite). Gestión asíncrona de pedidos, inventario y fiscalidad.

* **Frontend B2C Ultra-Premium**: Interfaz Single-Page (SPA) con navegación persistente y optimización para dispositivos táctiles.

* **Logística Inteligente**: Soporte completo para entrega a domicilio con validación de dirección y seguimiento en tiempo real.

* **Motor de Inteligencia (AI Insights)**: Integración con Gemini 1.5 Flash para el análisis de sentimientos de clientes y sugerencias operativas basadas en datos.

### 📦 Módulos Principales

1. **Punto de Venta (Quiosco)**: `/static/kiosko.html` - Interfaz rápida de autoservicio o mostrador.

2. **Cocina (KDS)**: `/static/kds.html` - Gestión visual de la línea de producción y tiempos de espera.

3. **BI de Producción**: `/static/dashboard_produccion.html` - Monitorización de KPIs operativos, mermas y rendimiento de productos.

4. **Admin Financeiro**: `/static/admin/dashboard.html` - Control de caja, Cierre Z y auditoría fiscal.

5. **Tracking del Cliente**: `/static/tracking.html` - Seguimiento visual del pedido para el usuario final.

### 🛠️ Configuración y Despliegue

* **Despliegue**: Optimizado para **Render** con persistencia en `instance/`.

* **PWA**: Instalable en cualquier dispositivo mediante `manifest.json` y `sw.js` v4.4.

* **Mantenimiento**: Scheduler integrado para limpiezas de logs y cierres automáticos a las 03:00 AM.

---

© 2026 Grupo Koal | Advanced Engineering for Retail
