# AGENTS.md - Instrucciones Principales para IA

- **Proyecto:** Carbones y Pollos TPV Enterprise
- **Ruta Local:** D:\proyecto\carbones_y_pollos_tpv
- **Negocio:** Carbones y Pollos La Granja S.L. (Restaurante, TPV, comida para llevar, delivery, caja).
- **CRÍTICO:** NO MEZCLAR bajo ninguna circunstancia con el proyecto 'GestiónKoal / gestion_avisos'.
- **Stack Técnico Detectado:** Python (FastAPI/Flask - ASGI uvicorn), SQLite (	pv_data.sqlite), HTML/JS/CSS vainilla (PWA), Render, GitHub.
- **Estructura Principal:** ackend/, static/, scripts/, 	ests/.
- **Comandos Principales:**
  - Iniciar local: watchdog_bridge.bat / uvicorn / gunicorn
  - Tests: pytest
- **Reglas de Trabajo:** Modificaciones incrementales, pruebas obligatorias locales antes de deploy.
- **Reglas de Seguridad:** No exponer GOOGLE_API_KEY, SECRET_KEY, ni tokens de Stripe en código o logs.
- **Reglas de Git:** Hacer commits pequeños y atómicos. No subir secrets ni .sqlite.
- **Reglas de Render:** Despliegue automático (rama main). Comprobar 
ender.yaml.
- **Archivos/Datos Delicados:** 	pv_data.sqlite, 
ender.yaml, ackend/main.py.
- **Qué leer primero:** docs/ai_context/PROJECT_CONTEXT.md y docs/ai_context/TASKS.md.
- **Obligación:** Actualizar CHANGELOG_AI.md y TASKS.md después de cada intervención.
