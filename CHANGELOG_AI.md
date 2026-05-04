# CHANGELOG AI - Carbones y Pollos TPV

Este archivo sirve como bitácora de todas las modificaciones realizadas por la Inteligencia Artificial (Agente) en el ecosistema de Carbones y Pollos TPV. Debe actualizarse después de cada tarea importante completada.

## Formato de Entrada

```markdown
### [YYYY-MM-DD] - [Título de la Tarea]
- **Descripción:** Breve resumen de lo que se hizo.
- **Archivos Modificados:** `archivo1.py`, `archivo2.js`
- **Agente:** [Nombre/Versión del Agente]
```

---

### [2026-05-03] - Industrialización de UI/UX y Navegación "Zero-Touch"

- **Descripción:** Auditoría y corrección de "enlaces ciegos" en la web pública. Creación de página legal unificada y conexión con footer. Optimización de la shell enterprise (V11.1) con detección automática de módulos y breadcrumbs. Implementación de motor de "Estados Vacíos" para mejorar la experiencia operativa ante la ausencia de datos.
- **Archivos Modificados:** `static/index.html`, `static/nosotros.html`, `static/legal.html`, `static/js/enterprise_shell.js`, `static/js/enterprise_ui.js`, `docs/ai_context/TASKS.md`.
- **Agente:** Antigravity (Gemini)

### [2026-05-03] - Blindaje RBAC y Estabilización de Infraestructura "Zero-Touch"

- **Descripción:** Implementación transversal de RBAC (Control de Acceso Basado en Roles) en routers críticos (`admin`, `orders`, `inventory`, `rrhh`, `telemetry`). Estabilización de servicios de background (`sync_daemon`, `local_printer_bridge`) mediante PID locking, gestión de colisiones y forzado de encoding UTF-8. Creación de herramientas maestras de recuperación (`master_restart.bat`).
- **Archivos Modificados:** `backend/routers/admin.py`, `backend/routers/orders.py`, `backend/routers/inventory.py`, `backend/routers/rrhh.py`, `backend/routers/telemetry.py`, `backend/routers/hardware.py`, `sync_daemon.py`, `local_printer_bridge.py`, `scripts/watchdog_bridge.py`.
- **Agente:** Antigravity (Gemini)

### [2026-05-03] - Industrialización de Impresión y Blindaje de IA

- **Descripción:** Se ha creado un script local (`local_printer_poller.py`) que permite consultar al backend en la nube e imprimir tickets físicamente en el local a través del mecanismo de `HardwareCommand`. Adicionalmente, se blindaron los prompts de `ai_assistant.py` y `ai_agent.py` para prevenir alucinaciones de la IA (obligando a ceñirse exclusivamente al inventario y precios reales).
- **Archivos Modificados/Creados:** `scripts/local_printer_poller.py`, `backend/routers/ai_assistant.py`, `backend/ai_agent.py`.
- **Agente:** Antigravity (Gemini)

### [2026-05-03] - Extracción del Contexto Técnico y Estandarización

- **Descripción:** Se ha creado una serie de 10 archivos `AI_*.md` (Context, API, DB, Hardware, Frontend, Business, Deploy, Env, Tasks) para almacenar toda la información operativa del negocio y la arquitectura del TPV, eliminando la dependencia de la memoria volátil de la IA y permitiendo que futuros agentes puedan integrarse y modificar el código de forma segura y sin alucinaciones. También se actualizó el `AGENTS.md`.
- **Archivos Modificados/Creados:** `AI_PROJECT_CONTEXT.md`, `AI_FILE_MAP.md`, `AI_DATABASE_CONTEXT.md`, `AI_API_ROUTES.md`, `AI_FRONTEND_CONTEXT.md`, `AI_DEPLOY_CONTEXT.md`, `AI_ENVIRONMENT_CONTEXT.md`, `AI_HARDWARE_CONTEXT.md`, `AI_BUSINESS_CONTEXT.md`, `AI_NEXT_TASKS.md`, `CHANGELOG_AI.md`.
- **Agente:** Antigravity (Gemini)

### 2026-05-04 - Finalización Auditoría TPV Operativa
- **orders.py**: Corrección de la lógica del cierre-z para utilizar el concepto de Jornada Comercial (04:00 UTC) y resolver los desfases de zona horaria de SQLite.
- **scripts/factory_reset.py**: Nuevo script creado para purgar en un solo paso los pedidos, items y cola de impresión de prueba (Factory Reset), manteniendo los catálogos y usuarios intactos.
- **static/kds.html**: Actualizada la UI de cocina para mostrar el estado y método de pago en badges dinámicos y condicionar la etiqueta del botón de acción según el estado actual.

### 2026-05-04 - Fix Tests y Seed (QA Pass 3/3)
- **Descripción:** Corrección de dos bugs críticos que bloqueaban CI: (1) `NameError: name 'Usuario' is not defined` en `scripts/seed_catalog_completo.py` — añadido import faltante. (2) Tests de telemetría devolvían 401 porque `conftest.py` no hacía override de `get_current_user` — añadido `mock_admin_user()` con `MagicMock(spec=Usuario)`. Resultado: 3/3 tests PASS.
- **Archivos Modificados:** `scripts/seed_catalog_completo.py`, `tests/conftest.py`.
- **Agente:** Antigravity (Claude Sonnet — Modo QA Revisora)
