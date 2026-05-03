# AI API ROUTES

## Visión General de la API

La API principal está construida con FastAPI, agrupada bajo el prefijo `/api`. Las dependencias y validaciones de tokens JWT se manejan en `backend/routers/dependencies.py` usando `get_current_user` y control de roles.

## Endpoints Clave Detectados (`backend/routers/`)

### Autenticación y Usuarios (`auth.py`)

- `POST /api/auth/token`: Login de usuario y retorno de JWT. (Público)
- `POST /api/auth/create_admin`: Script de escape para crear admin temporal. (Protegido/Público en demo)

### Catálogo e Inventario (`inventory.py`)

- `GET /api/inventory/categorias`: Lista categorías disponibles. (Público)
- `GET /api/inventory/productos`: Lista productos activos, puede filtrar por categoría. (Público)
- `GET /api/catalog/products`: Ruta alternativa detectada en legacy routers.
- `POST /api/inventory/productos`: Crea un nuevo producto (Requiere `ADMIN` / `MANAGER`).

### Pedidos (`orders.py`)

- `POST /api/orders/`: Creación de un pedido desde Kiosko / B2C. Retorna enlace a Stripe si requiere pago. (Público/Autenticado)
- `GET /api/orders/{pedido_id}`: Detalle del pedido.
- `GET /api/orders/kitchen/active`: KDS (Kitchen Display System), obtiene pedidos en preparación. (Requiere `CASHIER` o superior).
- `PATCH /api/orders/{pedido_id}/status`: KDS/Caja: Avanzar estado del pedido (Ej. `PREPARANDO` -> `LISTO`). (Protegido)

### Pagos y Webhooks (`webhooks.py`, `payments.py`)

- `POST /api/webhooks/stripe`: Recibe eventos de Stripe (pago completado). (Público, validado con secreto Stripe).
- `POST /api/webhooks/whatsapp`: Recibe mensajes entrantes del webhook de WhatsApp Cloud/WAHA. (Público, validado por WA/WAHA token).

### Caja y Gestión (`admin.py`, `commercial.py`, `rrhh.py`)

- `POST /api/admin/cierrez`: Realizar corte de caja/reporte Z diario. (Protegido `ADMIN`).
- `GET /api/admin/reportes`: Ver reportes pasados. (Protegido).

### Inteligencia Artificial (`ai_assistant.py`, `multi_agent.py`)

- `POST /api/ai/chat`: Envía prompt al modelo Gemini para atención comercial, consultando la carta. (Público/Autenticado según uso).
- `POST /api/ai/oracle/sync`: Comando de mantenimiento/multi-agente.

### KDS (Kitchen Display) y WebSockets (`ws.py`)

- `WS /ws/kitchen`: WebSocket para actualización en tiempo real del KDS.
- `WS /ws/kiosko`: WebSocket para notificaciones al cliente.

### Hardware (`hardware.py`)

- `POST /api/hardware/print/ticket`: Manda payload de impresión térmica al `local_printer_bridge`.
- `POST /api/hardware/print/kitchen`: Manda payload a la UROVO DP1201 (cocina).
- *(El puente físico debe conectarse a estos endpoints para hacer pooling, o bien la nube empuja al script puente local)*.

## ENDPOINTS FALTANTES RECOMENDADOS

- `GET /api/printer_status`: Endpoint para verificar si el puente `local_printer_bridge.py` está reportando como "vivo".
- `POST /api/inventory/stock_update`: Actualización rápida de stock físico.
