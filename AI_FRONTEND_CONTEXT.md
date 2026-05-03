# AI FRONTEND CONTEXT

## Tecnología y Stack
- **Arquitectura:** HTML Estático Servido por FastAPI + Vanilla JavaScript + TailwindCSS (vía CDN en algunos archivos o CSS precompilado).
- **PWA (Progressive Web App):** Sí. Incluye `manifest.json` y `sw.js` para ser instalable (ej. `INSTALAR_EN_ANDROID_TPV.bat`).
- **Naturaleza:** Diseñado como "Single Page Application" o "Multi-Page Estática" donde el DOM se manipula a través de módulos JS cargados dinámicamente (`EnterpriseShell`).

## Archivos y Pantallas Principales
- `static/portal.html` (o `index.html`): Archivo "Matrix" o Portal Cuántico. Sirve como hub de entrada principal. Contiene animaciones avanzadas, telemetría visual, y acceso a los módulos B2B (Admin, Caja, KDS, RRHH, Matrix, Fleet, etc.).
- `static/kiosko.html`: Interfaz orientada al consumidor (B2C) o Cajero puro. Es el "TPV táctil".
- `static/css/tailwind.css`: Estilos principales.
- `static/js/enterprise_shell.js` y `ui_components.js`: Controladores principales del DOM, modales e inyección de datos.

## Puntos Críticos y Flujos
- **TPV Mostrador / Kiosko (`kiosko.html` o modulo `tpv`):** Donde se ven las categorías y productos, carrito y cobro.
- **Cocina (KDS):** Accesible mediante el módulo `kds`. Recarga pedidos vía WebSockets o polling.
- **Caja (`caja`):** Interfaz para cobrar en efectivo/tarjeta y ver pedidos de la cola.
- **Conexión API:** Todo el front-end usa funciones nativas `fetch()` hacia `http://localhost:8000/api/...` o rutas relativas `/api/...`.
- **Adaptabilidad:** Tiene clases responsive de Tailwind (`md:grid-cols-4`, etc.). La tipografía principal es 'Outfit'. Tema oscuro predominante ("Deep Space").

## Mejoras Necesarias para Comida para Llevar
- **Velocidad Táctil:** El kiosko debe minimizar los clics. 
- **Flujo Offline:** Validar comportamiento del `sw.js` cuando el restaurante se queda sin internet.
- **Feedback Háptico / Sonoro:** Al entrar un pedido en KDS (Cocina), debe emitir un pitido fuerte.

## Acceso Esperado
- **Raíz / TPV B2C:** `http://localhost:8000/` -> sirviendo estático Kiosko/Portal.
- **Admin / Hub:** `http://localhost:8000/admin` o `http://localhost:8000/portal.html`.
- **Cocina KDS:** Lanzado desde el Portal -> Módulo `kds`.
