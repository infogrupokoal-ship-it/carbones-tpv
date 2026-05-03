# Estrategia de Backups Online (Carbones_TPV)

## Base de Datos (PostgreSQL)

- Cronjob en el VPS o funcionalidad nativa de Render/Neon para volcado diario `pg_dump`.

## Archivos Estáticos y Uploads

- Tarball diario de la carpeta `uploads/`.
