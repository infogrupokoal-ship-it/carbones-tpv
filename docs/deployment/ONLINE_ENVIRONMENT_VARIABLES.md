# Variables de Entorno Online (Carbones_TPV)

Estas variables deben configurarse en Render, VPS o GitHub Secrets. ¡NUNCA EN CÓDIGO! (Ver `.env.example`).

## Base de Datos
- `DATABASE_URL` (PostgreSQL. Ej: postgresql://user:pass@host:port/db)

## Inteligencia Artificial (Gemini)
- `GEMINI_API_KEY`
- `GOOGLE_API_KEY`
- `GEMINI_MODEL` (ej: gemini-1.5-flash)

## Integraciones y Seguridad
- `SECRET_KEY`
- `WAHA_URL`
- `WAHA_HTTP_API_KEY`
