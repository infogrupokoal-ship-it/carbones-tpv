# Monitorización y Gestión de Errores

## Healthcheck

Todos los proyectos deben exponer un endpoint `/healthz` o `/api/health` para que servicios externos comprueben su estado.

## Logs

- Render: Los logs están en el dashboard de Render.
- Local: Se recomienda guardar logs en `logs/` (ignorado en git).

## Sentry

Integración de Sentry recomendada para capturar excepciones no manejadas.
Añadir `SENTRY_DSN` a las variables de entorno.
