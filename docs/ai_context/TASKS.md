# TASKS.md

## 1. Crítico

- [x] Industrialización total de la UI del Kiosko B2C (Premium UX).
- [x] Sincronización de Base de Datos y Seeding Industrial.
- [x] Migración masiva de toda la suite Enterprise (Dashboard, RRHH, Caja, Liquidaciones, etc.) al 'Industrial Light Mode'.
- [x] Migración del sistema de navegación lateral a 'Accordion Submenus' táctiles optimizados para TPV.
- [x] Conexión de métricas BI (Stats & Analytics) a consultas SQL en tiempo real (eliminación de datos estáticos/mockeados).
- [x] Refactorizar `enterprise_shell.css` para soportar vista móvil (Sidebar overlay).
- [x] Optimizar `dashboard.html` para rejillas responsivas y tipografía escalable.
- [x] Implementar toggle de sidebar inteligente (Drawer en móvil, Collapse en Desktop).
- [x] Sincronizar tokens de diseño (`--sidebar-width`) entre JS y CSS.

## 2. Importante

- [x] Implementar sistema de repartidores y panel logístico (Fase 4.4 completada).
- [x] Implementar cálculo de nóminas y liquidaciones financieras para staff conectado a las Asignaciones de Reparto reales.
- [x] Integración de Carbonito AI en el Portal de Staff como asistente contextual.
- [x] Despliegue Zero-Touch en Render completado y sincronizado.

## 3. Mejora

- [x] Verificación de Portal de Staff y dashboards ejecutivos (100% operativos).
- [x] Refinar documentación del ecosistema (Actualizado CHANGELOG y arquitectura).

## 4. Futuro

- [ ] Revisar escalabilidad de SQLite a PostgreSQL en Render (si el volumen de ventas supera los 10k pedidos/mes).
- [ ] Conectar módulo de hardware local (impresoras/cajón de monedas) mediante agentes puente (WebSocket/Python local) en la sucursal física.

## Finalización de Industrialización (V5.0)
- [x] Integración final de componentes backend (Delivery Aggregators, Mantenimiento, Estadísticas BI reales).
- [x] Consolidación visual de todos los portales administrativos y comerciales a Enterprise Light Theme.
- [x] Corrección de dependencias y validación completa del startup de uvicorn.
- [x] Despliegue en Render verificado.

- [x] Integrar parseo NLP en el chat Carbonito del Kiosko B2C.
- [x] Corregir enlaces del Enterprise Shell hacia las vistas KDS y Fleet.

- [x] Desarrollar backend y frontend de Gestión de Franquicias (Franchise).
- [x] Desarrollar backend y frontend de Panel de Sostenibilidad (ESG).
- [x] Conectar módulos al Enterprise Shell.
* [x] Implementación completa V6.0 Enterprise (IoT, Crisis, ERP, Procurement, Menu Engineering).

## Fase VII: Industrialización Singularity (V7.0)
- [x] **Enterprise Shell v3.1**: Navegación por categorías colapsables (Accordion) y telemetría de latencia.
- [x] **Mass Injection Pipeline**: Automatización de la inyección del shell en 27 módulos industriales.
- [x] **Carbonito AI Business Analyst**: Integración en todos los módulos administrativos con contexto dinámico.
- [x] **KDS & Fleet Optimization**: Adaptación de layouts para visualización industrial en pantallas grandes.
- [x] **Render Production Sync**: Sincronización total de archivos estáticos y backend con la rama main.
- [x] **UI Audit & Fix**: Eliminación de duplicados visuales y restauración de lógica única por módulo.

## Fase VIII: Quantum Evolution (V9.0)
- [x] **Quantum Portal**: Nueva puerta de enlace centralizada para administración Enterprise.
- [x] **Predictive Analytics Portal**: Visualización BI avanzada con Chart.js y telemetría en tiempo real.
- [x] **Autonomous Dispatch Engine**: Motor de optimización logística con IA.
- [x] **Yield Pricing Engine**: Precios dinámicos basados en demanda y escasez.
- [x] **Robotics Telemetry Bridge**: Simulación y monitorización de hardware industrial de cocina.

## Fase IX: Quantum Singularity (V10.0)
- [x] Despliegue de Portal Quantum y Matrix Control.
- [x] Industrialización de Kiosko B2C con Carbonito AI.
- [x] Sincronización 100% de 37+ routers en backend.
- [x] Verificación de integridad de enlaces online.
- [x] Persistencia de datos en Render (/data).
- [x] **Quantum Portal V10**: Rediseño premium con estética industrial de alta fidelidad.
- [x] **Matrix Control (Digital Twin)**: Monitoreo visual de sistemas con logs neuronales en vivo.
- [x] **Kiosko V10 Upgrade**: Interfaz de cliente glassmorphism con Carbonito AI.
- [x] **Enterprise Shell V5**: Integración de Neural Link (Ctrl+J) y Command Palette (Ctrl+K).
- [x] **Global Link Audit**: 100% de integridad verificada en los 59 archivos del ecosistema.
- [x] **Full Infrastructure Sync**: Sincronización total de 37 routers y motores autónomos en Render.
- [x] **Final Singularity Audit**: Corrección de importaciones y enrutamiento modular completada.

## Fase X: Singularity Industrialization (V9.3)
- [x] **Self-Healing Engine [V6.0]**: Implementación de protocolos Omega/Sigma para recuperación automática de BD y activos.
- [x] **BI Stats Optimization**: Corrección de tipos de datos SQLAlchemy y cast de fechas para analítica precisa.
- [x] **IoT Hardware Stabilization**: Sincronización de modelos de logs operativos con el puente de telemetría.
- [x] **Logística Legacy Support**: Adición de endpoints de compatibilidad (/orders/active) para apps móviles.
- [x] **Unicode Sanitization**: Eliminación de emojis conflictivos para estabilidad en consolas Windows legacy.
- [x] **Loyalty Portal [V6.0]**: Implementación completa del sistema de puntos y niveles VIP industriales.
- [x] **Production Ready Audit**: Creación de la lista de verificación final para despliegue zero-touch en Render.

## Fase XI: B2C Storefront & Backend Stabilization [V11.0]
- [x] **B2C Primary Entry**: Configuración de `index.html` como raíz (`/`) para priorizar la venta directa.
- [x] **Admin Decoupling**: Movimiento del portal administrativo a `/admin` para separación clara de contextos.
- [x] **Circular Import Resolution**: Desacoplamiento de `auth.py` y `admin_audit.py` mediante importaciones diferidas.
- [x] **Path Robustness**: Implementación de rutas absolutas en `main.py` para localización de activos estáticos.
- [x] **Visual Audit Completion**: Verificación de integridad de UI tanto en el catálogo B2C como en el dashboard administrativo.

## Fase XII: Industrial Singularity Reinforcement [V11.5]
- [x] **RBAC Gatekeeping**: Implementación de escoltas de ruta y pantallas de acceso denegado en Enterprise Shell.
- [x] **DOM Shielding**: Ocultación y eliminación dinámica de elementos sensibles basada en roles (data-role).
- [x] **Carbonito Contextual**: Mejora de la IA para recibir y procesar el contexto operativo (ruta/módulo) en tiempo real.
- [x] **Neural Monitor Logs**: Integración de logs del sistema real en la consola de telemetría (Ctrl+J).
- [x] **Kiosko Polish**: Resolución de 404s de imagen y mejora de la estética profesional del catálogo B2C.

## Fase XIII: Supermega Singularity [V12.0]
- [x] **AI Proactive BI**: Implementación de motor de insights proactivos basados en flujo de datos real.
- [x] **Digital Twin Matrix**: Visualización 360° de nodos de hardware e infraestructura IoT.
- [x] **Quantum Loyalty**: Portal de fidelización gamificado para expansión de marca y retención.
- [x] **Industrial UX+**: Integración de feedback auditivo y visualización de carga neuronal en tiempo real.
- [x] **Final 20x Professionalization**: Auditoría total y sincronización global en Render.
## Fase XIV: Autonomous Proactive Intelligence [V13.0]
- [x] **AuditLog Consolidation**: Unificación del esquema industrial y eliminación de redundancias estructurales.
- [x] **Zero-Touch Seeding**: Implementación de inyección automática de catálogo industrial en primer arranque.
- [x] **AI Real-Time Awareness**: Inyección de logs operativos (LogOperativo) en el contexto de Carbonito AI.
- [x] **Telemetry Sync**: Resolución de rutas de telemetría para Matrix Dashboard (/api/telemetry/advanced).
- [x] **Persistent Stock Guard**: Registro automático de alertas críticas de inventario en logs operacionales.
- [x] **Industrial Recovery Tool**: Creación de script de fuerza bruta para reset y sembrado de base de datos (`force_seed.py`).

## Fase XVI: Advanced Multi-Agent Oracle [V15.0]
- [x] **Agent Specialization**: Separación de lógica en Agente Business (Ventas) y Agente Auditor (Seguridad).
- [x] **Strict Schema Enforcement**: Implementación de `response_mime_type="application/json"` en el `GeminiProvider`.
- [x] **Markdown Stripper**: Sistema de sanitización para eliminar bloques de código Markdown generados por la IA.
- [x] **Executive UI Rendering**: Transformación del JSON estructurado a HTML visual con emojis y listas de impacto en `portal.html`.
- [x] **E2E Anomaly Seeding**: Creación de `seed_audit_data.py` para generar fraudes y pruebas de esfuerzo para los agentes.
- [x] **Clean Code Audit**: Resolución de variables huérfanas en `multi_agent.py` logrando 0 errores en `ruff check`.

## Fase XVII: Full Industrial Hardening & Autonomous Stability (V16.0)
- [x] **Linting Zero-Tolerance**: Elimination of all critical E/F violations across the entire codebase.
- [x] **Lifespan Migration**: Modernization of FastAPI startup/shutdown handlers.
- [x] **Windows encoding fix**: Global enforcement of UTF-8 in stdout/stderr and logging handlers.
- [x] **Model Integrity**: Resolution of schema mismatches in `multi_agent` and `stats` routers.
- [x] **Operational Boot Validation**: 100% healthy backend startup verified locally.
