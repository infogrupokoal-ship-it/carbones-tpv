# OPENCLAW_CONTEXT.md

- **Objetivo:** Guiar al agente local/VPS para interactuar con Carbones TPV.
- **Acciones Permitidas:** Leer archivos, ejecutar scripts de test (pytest), inspeccionar logs.
- **Acciones Prohibidas:** Modificar archivos fuera de carbones_y_pollos_tpv, destruir DB, hacer deploys destructivos.
- **Verificación:** Ejecutar pwd y git status como primeras acciones siempre.
