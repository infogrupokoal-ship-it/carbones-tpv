# DOCUMENTO DE ARQUITECTURA Y CONTRATO DEL PROYECTO (PROJECT CONTRACT)

**Proyecto:** TPV Enterprise "Carbones y Pollos"
**Versión de Arquitectura:** 5.0 (Zero-Touch Print Ecosystem)
**Fecha de Revisión:** Mayo 2026

## 1. VISIÓN EJECUTIVA Y OBJETIVOS DE NEGOCIO

El ecosistema TPV de Carbones y Pollos tiene como objetivo primordial operar bajo un paradigma de **"Zero-Touch Maintenance" y "24/7 Autonomous Reliability"**. El software debe trascender la categoría de TPV tradicional para convertirse en un ERP operativo ligero e infalible, capaz de gestionar alta concurrencia en retail (Caja Maestra), movilidad en tienda (Tabletas TPV) y flujos orquestados en cocina (KDS). La estabilidad y la inmutabilidad de los flujos críticos de facturación e impresión son innegociables.

## 2. ARQUITECTURA TÉCNICA BASE

### 2.1 Backend (Motor API & Datos)

- **Framework Core:** FastAPI (ASGI) operando sobre Python 3.11+.
- **Motor de Base de Datos:**
  - **Local/Desarrollo:** SQLite3 (base `tpv_data.sqlite`) con activaciones PRAGMA estrictas (WAL mode, Foreign Keys ON).
  - **Producción (Render):** PostgreSQL vía SQLAlchemy ORM / Asyncpg (en migración).
- **Control de Acceso y RBAC:** Autenticación JWT con rotación de tokens y cifrado asimétrico. Niveles estrictos de acceso (Admin, Manager, Operador).

### 2.2 Frontend (Interfaz y Experiencia de Usuario)

- **Framework:** Vanilla JS / HTML5 semántico (eliminación de dependencias reactivas pesadas para maximizar rendimiento en dispositivos embedded).
- **Estilos:** Framework utilitario (TailwindCSS) complementado con librerías CSS industriales personalizadas (`premium_industrial.css`).
- **PWA (Progressive Web App):** Service workers habilitados para manejo de caché de assets, funcionamiento off-line parcial y resiliencia ante cortes de conectividad.

## 3. ARQUITECTURA DEL ECOSISTEMA DE IMPRESIÓN (PRINT INFRASTRUCTURE)

La gestión de impresión exige un aislamiento estricto entre el motor de la base de datos y la capa de hardware. El objetivo es eliminar cualquier ventana de diálogo o intervención manual por parte del operador de caja/tienda.

### 3.1 Entornos Windows / Legado (Dual-Fallback Strategy)

- **Componente:** `local_print_bridge.py` (Flask micro-server local).
- **Flujo:** La API enruta los *Print Jobs* a `127.0.0.1:8181`. El bridge recibe un payload estructurado JSON + HTML crudo.
- **Ejecución:** Invoca silenciosamente a la impresora térmica por defecto utilizando rutinas de PowerShell y automatización en background.

### 3.2 Entornos Android TPV Móviles (Arquitectura Primaria)

- **Infraestructura Objetivo:** Cola de trabajos (Print Queue) persistida en base de datos.
- **Protocolo de Impresión Nativa:** Uso exhaustivo de **Intents URL de Android** (`intent://#Intent;scheme=rawbt;package=ru.a402d.rawbtprinter;end;`).
- **Flujo Asíncrono Completo:**
  1. Frontend TPV despacha el requerimiento a `/api/print/jobs`.
  2. Backend almacena el trabajo y retorna un `job_id`.
  3. Frontend codifica el contenido (Base64) y dispara el Intent hacia la aplicación **RawBT**.
  4. RawBT procesa en background (sin diálogo) e interroga a la impresora Bluetooth/USB.
  5. *Poll/Ack:* El frontend (o un service worker) envía la confirmación al backend vía webhook o endpoint de ACK (`/api/print/jobs/{id}/ack`).

## 4. SISTEMA VISUAL Y GUÍA DE ESTILO (DESIGN SYSTEM)

El diseño debe comunicar robustez, profesionalismo y eficiencia.

- **Acento Corporativo:** `#facc15` (Amarillo Ámbar Carbones).
- **Paleta de Estados Semánticos de Impresión:**
  - `QUEUED` / Pendiente: Ámbar pálido (esperando encolado).
  - `PROCESSING` / En curso: Azul corporativo (enviado a hardware).
  - `PRINTED` / Exitoso: Verde esmeralda oscuro (hardware ACK validado).
  - `ERROR` / Fallo: Rojo carmesí intenso con iconografía de advertencia.
- Toda vista nueva debe heredar componentes de `static/js/ui_components.js`.

## 5. REGLAS DE DESPLIEGUE Y OPERACIÓN (CI/CD / RENDER)

1. **Regla de Cero Pérdidas:** Las modificaciones en el esquema de la base de datos deben incluir un script de migración *Alembic* o un script de parche (`fix_schema.py`) explícito.
2. **Validación de Integridad:** Se requiere validación sintáctica estricta antes de commitear en la rama `main` o derivaciones.
3. **Impresión Segura:** NUNCA asumir conectividad directa con impresora en Render. Render ejecuta el backend; el cliente despacha los comandos a su entorno local mediante la cola de trabajos. Las variables de entorno `PRINT_MODE` y `LOCAL_PRINTER_URL` deben estar debidamente documentadas y mapeadas en el `render.yaml`.
