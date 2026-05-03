# AI DEPLOY CONTEXT

## Entorno de Producción Principal (PaaS)
El despliegue está configurado para la plataforma **Render** (`render.com`).

### Resumen de `render.yaml`
- **Tipo:** Web Service.
- **Nombre:** `carbones-tpv`
- **Entorno Base:** Python 3.11.8.
- **Plan:** Free (`free`).
- **Región:** Frankfurt.
- **Build Command:** `pip install --upgrade pip && pip install -r requirements.txt`
- **Pre Deploy Command:** `python scripts/migrate_v5.py && python scripts/seed_ultra.py` (Asegura base de datos correcta en cada despliegue).
- **Start Command:** `gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.main:app --bind 0.0.0.0:$PORT`
- **Healthcheck:** `/api/health`

### Almacenamiento Persistente
- Render utiliza un **Persistent Disk**.
- **Nombre:** `tpv-data-storage`
- **Punto de montaje:** `/data`
- **Tamaño:** 1 GB.
- *Nota vital:* La DB local es `./tpv_data.sqlite`, pero en render se inyecta `DATABASE_URL=sqlite:////data/tpv_data.sqlite` para asegurar persistencia.

## Entorno Alternativo: VPS Kamatera / Local Server
Existen scripts para un posible despliegue en máquina física (servidor propio):
- `deploy_kamatera.bat`
- `docker-compose.yml` (Contiene infra Docker).
- `Procfile` (Útil para Heroku/VPS).

## Checklist y Riesgos
- [ ] **Deploy Local:** Asegurarse de tener un entorno `.venv`, correr `pip install -r requirements.txt` y ejecutar el `watchdog_bridge.bat`.
- [ ] **Deploy Render:** Subir a GitHub en la rama `main` activa el auto-deploy en Render.
- [ ] **Variables Render:** Configurar `SECRET_KEY`, `GEMINI_API_KEY`, y otras expuestas en el `.env`.
- [ ] **Riesgo SQLite Locked:** En producción real de alta carga (TPV + B2C simultáneo intenso), SQLite puede lanzar errores de bloqueo de escritura (Database is locked). Monitorizar `/api/health` latencia.
