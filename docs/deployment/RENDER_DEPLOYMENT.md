# Despliegue en Render (Carbones_TPV)

## Revisión del `render.yaml`
Se debe contar con un archivo `render.yaml` que defina:
- **Build Command:** `pip install -r requirements.txt` (Migraciones requieren acción manual o script seguro).
- **Start Command:** Comando de arranque del servidor.
- **Auto Deploy:** Activo al hacer push a `main`.

## Rollback
Si el último deploy es verde pero falla la app, ir al dashboard de Render y seleccionar "Deploy previous commit".
