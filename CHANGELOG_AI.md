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
