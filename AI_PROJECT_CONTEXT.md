# AI PROJECT CONTEXT

## Información General

- **Nombre Real del Proyecto:** Carbones y Pollos TPV Enterprise
- **Ruta Exacta Local:** `D:\proyecto\carbones_y_pollos_tpv`
- **Lenguaje Principal:** Python 3.13.5
- **Framework Backend:** FastAPI (v0.110.0) + Uvicorn
- **Framework Frontend:** HTML Estático / Vanilla JS / CSS (TailwindCSS vía CDN) + PWA (manifiesto/service worker).
- **Base de Datos:** SQLite (archivo `tpv_data.sqlite`).

## Ejecución Local

- **Arranque:** Ejecutando `watchdog_bridge.bat` (recomendado) o `python backend/main.py`.
- **Puerto Local:** `8000` por defecto.
- **Pruebas (Tests):** Se usa `pytest` (ej: `python -m pytest tests/`).
- **Punto de Entrada API:** `http://localhost:8000/api`
- **Frontend Local:** `http://localhost:8000/` o abriendo directamente `static/portal.html`.

## Estructura de Carpetas Clave

- `backend/`: Código de la API FastAPI, modelos, routers y lógica de negocio.
- `static/`: Archivos del frontend (HTML, CSS, JS, sw.js).
- `scripts/`: Herramientas auxiliares, seeds (ej. `seed_ultra.py`) y migraciones automáticas.
- `tests/`: Conjuntos de pruebas.
- `instance/` / `logs/`: Logs y bases de datos generadas (basura/datos dinámicos).
- `docs/`: Documentación del proyecto (Markdown).

## Estado del Proyecto

- **Partes Funcionando (Producción-ready):** API base, base de datos SQLite con SQLAlchemy, estructura de autenticación, webhooks de pagos (Stripe), endpoints base de IA, render.yaml funcional, integración CI/CD rudimentaria.
- **Partes Incompletas / Por Terminar:** Integración física de hardware en TPV táctil local (impresoras), WhatsApp bidireccional (bot completo), y caja fuerte local (reporte Z estricto físico). Frontend PWA táctil está en fase de refinamiento.
- **Riesgos:** La base de datos es SQLite (`tpv_data.sqlite`). Si se sube a Render sin un "disk" persistente, los datos se borran. Actualmente Render usa un `disk` llamado `tpv-data-storage`. Otro riesgo son los scripts locales `.bat` y `.sh` que no funcionarán en Render.

## Git y Versiones

El proyecto tiene inicializado Git.

- **Remote:** `origin https://github.com/infogrupokoal-ship-it/carbones-tpv.git`
- **Branch Actual:** `main` (alineado con origin/main).
- **Últimos Commits:**
  - `98d8052` (refactor datetime.utcnow a timezone-aware)
  - `51f7a74` (feat ai sync model config)
  - `691b1ce` (Fix circular imports y 404)
