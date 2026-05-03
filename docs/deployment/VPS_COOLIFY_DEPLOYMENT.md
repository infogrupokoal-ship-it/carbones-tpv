# Despliegue en VPS / Coolify (Carbones_TPV)

## Arquitectura Docker
Si se usa Coolify o Docker-compose directo en VPS:
- Servicio Web: App Flask/FastAPI.
- Servicio DB: PostgreSQL (Neon / VPS).
- Servicio WAHA: Instancia separada exponiendo puerto interno 3001.

## Configuración Red Interna
Los puertos de la DB y WAHA **NO** deben estar expuestos a internet (0.0.0.0), solo la app web o el Nginx/Traefik Reverse Proxy.
