# ARCHITECTURE.md

- **Stack Técnico:** Backend en Python (probablemente FastAPI o Flask con Uvicorn/Gunicorn), Frontend Vanilla (HTML, CSS, JS) como PWA.

- **Base de Datos:** SQLite (    pv_data.sqlite).

- **APIs/Integraciones:** Stripe (Pagos), WhatsApp (bot/twilio), Google Generative AI (Carbonito).

- **Rutas Principales:** / (Portal), /kiosko.html, /caja.html, /cocina.html (KDS), /admin/dashboard.html.

- **Flujo de Datos:** El cliente pide en Kiosko -> El pedido viaja al Backend (SQLite) -> Se muestra en KDS (Cocina) -> Se cobra en Caja/Stripe.

- **Dependencias Importantes:** uvicorn, gunicorn, sqlalchemy/sqlite3, google-generativeai.
