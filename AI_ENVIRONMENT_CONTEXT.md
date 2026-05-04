# AI ENVIRONMENT CONTEXT

## Resumen de Variables (Detectadas en `.env.example` y Código)

Formato: `VARIABLE` = Función / Requerida / Entorno / Riesgo

- `APP_NAME` = Nombre del sistema / Opcional / Todos / Ninguno
- `APP_VERSION` = Versión actual / Opcional / Todos / Ninguno
- `ENVIRONMENT` = `production` o `development` / Requerida / Todos / Si falta, asume development (puede exponer errores).
- `DEBUG` = Activar trazas profundas / Opcional / Local / Exposición de secretos si está en true en Producción.
- `DATABASE_URL` = Cadena de conexión / Requerida / Todos / Riesgo crítico (Si falta, el sistema no arranca o crea una en memoria).
  - *Local:* `sqlite:///./tpv_data.sqlite`
  - *Render:* `sqlite:////data/tpv_data.sqlite`
- `SECRET_KEY` = Firma JWT y Sesiones / Requerida / Todos / CRÍTICO. Si es débil, las cuentas son vulnerables.
- `CORS_ORIGINS` = Dominios permitidos / Requerida / Render / CRÍTICO. Protege la API de ataques de dominios cruzados.
- `GOOGLE_API_KEY` o `GEMINI_API_KEY` = Acceso a IA de Gemini / Opcional (Requerida para Módulo IA) / Render / Falla asistente IA si no está.
- `VPS_URL` = IP del servidor físico o Kiosko para bridge / Opcional / Render.
- `LOCAL_PRINTER_URL` = IP interna del TPV Windows para enviar colas de impresión térmica / Opcional / Render / Falla ticket en local.
- `AUTO_Z_CLOSE_TIME` = Hora de cierre de caja automático (ej "03:00") / Opcional.
- `MAX_LOG_AGE_DAYS` = Rotación de logs / Opcional.
- `WAHA_URL` / `WAHA_HTTP_API_KEY` = Conexión WhatsApp API / Opcional (Requerida para pedidos WA).

> [!WARNING]
> Nunca subir el archivo `.env` a GitHub. Usar el dashboard de variables de entorno de Render para setear producción.
