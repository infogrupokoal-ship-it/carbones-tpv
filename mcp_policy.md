# MCP Policy

## Permisos Mínimos

- Filesystem: Limitado al directorio del proyecto activo.
- Shell: Allowlist de comandos seguros (git, ls, find, grep, mkdir, uvicorn, pytest, docker logs).
- Git: Prohibido `force push`.
- DB: Read-only por defecto para auditorías; write requiere permiso para cambios estructurales.
- WhatsApp: No enviar mensajes reales sin confirmación de la IA Revisora o Jorge.

## Kill Switch

Si se detecta comportamiento errático o gasto masivo de tokens, detener la ejecución y avisar a Jorge.
