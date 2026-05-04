# Política de Autonomía IA

## Comandos Seguros (Permitidos sin confirmación)

- `dir`, `ls`, `git status`, `git diff`, cat, grep (búsquedas seguras).
- Ejecución de linters (`ruff`, `bandit`) y tests (`pytest`).
- Modificación de archivos de documentación y scripts en `tools/ai_agents/`.
- Creación de copias de seguridad vía `tools/backups/`.

## Comandos Sensibles (Requieren Aprobación)

- Modificación directa de la Base de Datos (`.sqlite`).
- `docker-compose down -v` o borrado de volúmenes.
- Re-escrituras grandes de historia git (`reset --hard`, `push -f`).
- Despliegues directos a producción sin pasar por Render hooks.

> [!CAUTION]
> NUNCA exponer `SECRET_KEY` o variables reales de `.env` en los outputs o repositorios.
