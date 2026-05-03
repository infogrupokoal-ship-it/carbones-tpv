# Healthchecks (Carbones_TPV)

El endpoint de healthcheck debe ejecutar lógica:
1. SELECT 1 de la base de datos PostgreSQL.
2. Ping interno al puerto de WAHA.
3. Devolver JSON: `{"status": "ok", "db": "ok", "waha": "ok"}`
