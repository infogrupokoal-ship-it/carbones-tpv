# AI FILE MAP

## Mapa de Archivos Relevantes del Proyecto

### Raíz del Proyecto

- `backend/main.py`: Entrada principal de FastAPI. Conecta routers, middlewares, DB y sirviendo estáticos. Activo y muy importante.
- `render.yaml`: Configuración de despliegue en la plataforma Render. Producción.
- `requirements.txt`: Dependencias de Python. Activo.
- `watchdog_bridge.bat` / `Procfile`: Scripts de arranque para local y servidor respectivamente.

### Backend (`backend/`)

- `database.py`: Configuración base de datos (SQLAlchemy engine/Session).
- `models.py`: Modelos ORM completos (Usuarios, Productos, Tienda, Pedidos, Mermas, Logs). Muy importante. Riesgo alto al modificar (puede romper SQLite).
- `auto_migrate.py`: Ejecuta migraciones rudimentarias usando SQLAlchemy de los modelos definidos, comprobando tablas.
- `config.py`: Carga y validación de variables de entorno usando `pydantic-settings`.
- `routers/`:
  - `orders.py`, `inventory.py`, `admin.py`, `customers.py`: APIs principales de la app TPV.
  - `ai_assistant.py`, `multi_agent.py`: Lógica IA y endpoints Gemini.
  - `webhooks.py`: Endpoints para recepción de Stripe y WhatsApp.
  - `hardware.py`: Puente para comandos de impresoras de la tienda física.
- `utils/`:
  - `logger.py`: Logging universal.
  - `ai_model_manager.py`: Configuración dinámica Gemini/IA.

### Scripts (`scripts/`)

- `seed_ultra.py`: Crea datos iniciales (tienda, usuarios admin, catálogo base) en base de datos vacía. Idempotente.
- `seed_catalog_completo.py`: Popula la base de datos con la carta nocturna completa.

### Frontend (`static/`)

- `portal.html` / `index.html`: Punto de entrada del Kiosko / TPV y admin web.
- `sw.js` / `manifest.json`: Archivos para la PWA (Progressive Web App).
- *(Normalmente aquí irían CSS custom o JS adicionales, pero gran parte puede estar embebido vía Tailwind CDN en los HTML).*

### Hardware Local

- `local_printer_bridge.py`: Archivo que se ejecuta localmente en el TPV físico Windows de la tienda para hacer puente entre la API en Render y las impresoras locales (USB/Red).

### Docs (`docs/`)

- Contiene todo el historial de IA (AGENTS.md, AI_MASTER_CONTROL_BOOK.md, etc.) que dicta las reglas del ecosistema.
