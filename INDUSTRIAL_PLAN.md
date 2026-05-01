# 🛠️ Plan Maestro de Industrialización Retail v4.4

Este documento detalla el blindaje técnico y operativo aplicado al ecosistema **Carbones y Pollos TPV** para su operación en entornos reales de producción.

## 1. Governance & Seguridad
*   **Auditoría Inmutable**: Cada acción administrativa (Cierre Z, cambios de stock) se registra en `tpv_data.sqlite` con IP y marca de tiempo.
*   **Enfoque Zero-Trust**: La base de datos y los logs se almacenan en un volumen persistente separado en Render (`instance/`).

## 2. Resiliencia Operativa (Offline-First)
*   **Service Worker v4.4**: Caché inteligente de activos estáticos para permitir la carga del TPV incluso con conectividad inestable.
*   **Local Storage Sync**: Los pedidos del KDS se respaldan localmente para evitar pérdida de datos ante caídas de red momentáneas.

## 3. Logística de Domicilio (Retail 360)
*   **Validation Layer**: Los pedidos `DOMICILIO` requieren Calle y CP válidos.
*   **Fiscalidad Integrada**: Las tasas de envío se calculan en el backend con IVA del 10% para cumplimiento legal en España.
*   **KDS Delivery Badge**: Marcado visual de pedidos de domicilio para el personal de cocina.

## 4. Automatización & IA
*   **Scheduler Nocturno**: Purga automática de logs de >30 días y Cierre Z de emergencia a las 03:00 AM.
*   **Gemini Business Advisor**: Análisis NLP de las reseñas de clientes para detectar tendencias negativas antes de que afecten al margen.

## 5. Próximos Pasos (Hoja de Ruta)
*   [ ] Integración total con pasarela Stripe para pagos online.
*   [ ] App nativa para repartidores con geolocalización real.
*   [ ] Sistema de lealtad con monedero virtual.

---
*Generado automáticamente por Antigravity AI Engine.*
