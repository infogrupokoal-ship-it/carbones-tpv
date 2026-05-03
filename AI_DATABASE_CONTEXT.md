# AI DATABASE CONTEXT

## Motor y Configuración
- **Motor:** SQLite en local. PostgreSQL recomendado para Producción, aunque el Render.yaml actual indica `sqlite:////data/tpv_data.sqlite` en un Persistent Disk de Render de 1GB.
- **ORM:** SQLAlchemy (v2+).
- **Migraciones:** Alembic está instalado, pero parece que el proyecto usa un script `auto_migrate.py` y `scripts/migrate_v5.py` para sincronizar las columnas sin alembic puro.

## Modelos y Tablas Detectados (`backend/models.py`)

- **Multitenancy y Configuración Base**
  - `Tienda` (tiendas): id, nombre, direccion, configuraciones industriales (lat, lon, color_primario).
  - `Usuario` (usuarios): id, username, rol, pin_hash.

- **Catálogo, Recetas e Inventario**
  - `Categoria` (categorias): id, nombre.
  - `Producto` (productos): id, nombre, precio, stock_actual, turno_disponible, categoria_id, etc.
  - `Ingrediente` (ingredientes): stock, proveedor, ud.
  - `Proveedor` (proveedores) y `RecetaItem` (receta_items).

- **Ventas, Caja y Cierres**
  - `Pedido` (pedidos): numero_ticket, total, metodo_pago, estado, origen (TPV), metodo_envio, stripe_session_id.
  - `ItemPedido` (item_pedido): FK a pedidos y productos.
  - `ReporteZ` (reportes_z): Cierre de caja, ventas, efectivo, mermas.
  - `MovimientoStock` (movimientos_stock): Entradas/salidas trazables.
  - `Merma` (mermas): Caducado, rotura.

- **Clientes y Marketing**
  - `Cliente` (clientes): telefono, nombre, fidelidad.
  - `Referido` (referidos).
  - `Review` (reviews).

- **IA y Automatización**
  - `AIConfig` (ai_configs): Configuraciones dinámicas de modelos.
  - `AgentMessage` (agent_messages): Comunicación entre agentes de software autónomos.

## Estado de los Datos
- **Seeds:** Existe `seed_ultra.py` que asegura que hay una Tienda y un Usuario administrador. Existe `seed_catalog_completo.py` (Carta nocturna real, bocadillos, chivitos).
- **Datos Reales vs Demo:** El catálogo incluye productos reales (chivito de pollo a 6.50, brascada, etc.), pero las ventas en local son pruebas.
- **Campos de Pagos:** Pedidos incluye `metodo_pago` y soporta `stripe_session_id`.
- **Campos de KDS / Cocina:** `Pedido.estado` maneja "ESPERANDO_PAGO", "PREPARANDO", etc.
