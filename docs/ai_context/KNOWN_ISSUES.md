# KNOWN_ISSUES.md

- **Errores de Configuración:** Posibles errores 404 en el bot de WhatsApp si el modelo de IA falla o cambia de versión (mitigado recientemente según git log).

- **Render:** Render free tier puede dormir la aplicación; requiere healthchecks o pings periódicos.

- **Zonas Críticas:** ackend/main.py y     pv_data.sqlite. La IA no debe improvisar con la estructura de la base de datos sin revisar scripts de migración.
