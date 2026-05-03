# Monitorización Online (Carbones_TPV)

## Endpoints Vitales
- `/healthz`: Debe devolver 200 OK y comprobar conexión a BD.

## Herramientas
- **UptimeRobot / Better Stack:** Hacer ping a `/healthz` cada 5 min.
- **Sentry:** Integrado en código para captura de trazas de errores.
