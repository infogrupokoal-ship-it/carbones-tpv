# RENDER_DEPLOYMENT.md

- **Estado:** Configurado vía 
ender.yaml.
- **Servicio:** carbones-tpv-enterprise (Web Service, Frankfurt).
- **Rama:** main.
- **Build Command:** pip install --upgrade pip && pip install -r requirements.txt
- **Start Command:** gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.main:app --bind 0.0.0.0:
- **Variables Críticas:** PYTHON_VERSION, DATABASE_URL, GOOGLE_API_KEY, SECRET_KEY, ENVIRONMENT.
- **Prohibición:** No modificar variables ni forzar deploys manuales sin permiso explícito.
