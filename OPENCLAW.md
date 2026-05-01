# OPENCLAW.md - Instrucciones para el Agente Local/VPS

- **ATENCIÓN:** Este proyecto es completamente independiente. Corresponde a Carbones y Pollos.
- **Paso 1:** Leer AGENTS.md antes de tocar nada.
- **Paso 2:** Leer docs/ai_context/OPENCLAW_CONTEXT.md.
- **Verificaciones obligatorias:**
  - Ruta: Verificar con pwd que estás en D:\proyecto\carbones_y_pollos_tpv (o la ruta correspondiente en VPS).
  - Rama: Verificar con git branch.
  - Cambios: Verificar con git status.
- **Restricciones:**
  - NO aplicar instrucciones ni contexto de GestiónKoal.
  - NO borrar la base de datos 	pv_data.sqlite.
  - NO borrar volúmenes de Docker.
  - NO ejecutar comandos destructivos (
m -rf, git reset --hard) sin permiso explícito del usuario.
- **Documentación:** Toda intervención debe registrarse en CHANGELOG_AI.md.
