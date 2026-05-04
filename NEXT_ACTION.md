# NEXT ACTION (EXECUTION PROTOCOL)

## Tarea Crítica Inmediata: Modificación Estructural de Base de Datos y Modelos

**Estado:** PENDIENTE DE INICIO
**Criticidad:** ALTA (Bloqueante para el resto del Sprint)

### Pasos Estrictos a Ejecutar

1. **Auditoría de Esquema Actual:**
   - Inspeccionar el archivo `backend/database.py` o módulo equivalente de SQLAlchemy/SQLite para mapear cómo se inicializan las tablas actualmente.
2. **Creación del Modelo Pydantic / SQLAlchemy:**
   - Crear la entidad `PrintJob` en el código.
   - Campos obligatorios: `id` (String UUID/Autoincrement), `created_at` (DateTime, default UTC now), `payload` (Text/String, JSON/Base64 con los datos a imprimir), `target_device` (String, opcional), `status` (String, default `PENDING`).
3. **Mecanismo de Migración Cero-Pérdida:**
   - Modificar el script de arranque o crear un script `migrate_print_queue.py` que añada la tabla de manera segura (ej. `CREATE TABLE IF NOT EXISTS print_jobs (...)`).
   - Validar que la tabla existe utilizando SQLite local antes de hacer push.
4. **Desarrollo del Router:**
   - Crear/modificar `backend/routers/print_queue.py` (o similar).
   - Enganchar los endpoints al ciclo de vida global en `backend/main.py`.
5. **Validación Exhaustiva:**
   - Arrancar el motor en local.
   - Enviar un requerimiento HTTP `POST` a la nueva cola de impresión usando `Invoke-RestMethod` o `curl`.
   - Recuperarlo con un `GET` HTTP.

**Aprobación Requerida:** Tras aplicar estos cambios de backend, el agente deberá detenerse, realizar un `commit` si la validación es exitosa (`git status`, `git add`, `git commit -m "feat(print): add database models and queue endpoints"`), reportar al Arquitecto y quedar a la espera del visto bueno para iniciar la Fase 2 (Frontend JS Poller).
