# Arquitectura de Despliegue Online (Carbones_TPV)

## Entornos
1. **Local:** Desarrollo y pruebas exclusivas (SQLite permitido y mantenido).
2. **Staging (Pruebas Online):** Entorno idéntico a producción pero con datos dummy.
3. **Producción (Main):** Entorno real. PostgreSQL obligatorio. ¡NO se ejecutarán migraciones de producción sin confirmación!

## Dominios Previstos
- carbones-tpv.onrender.com
- tpv.carbonesypollos.com
- pedidos.carbonesypollos.com

## Estrategia Git
- Rama `main` -> Producción automatizada (o vía PR).
- Rama `staging` (opcional) -> Despliegue de prueba.
