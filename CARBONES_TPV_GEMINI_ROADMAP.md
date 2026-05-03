# Roadmap Gemini Multi-Agente: Carbones y Pollos TPV

## Arquitectura Recomendada
- **Gemini Flash JSON Mode:** Extraer rápidamente comandas por voz si los operarios hablan a la tablet.
- **Gemini Pro Data Analysis:** Analizar SQLite `tpv_data.sqlite` exportado a CSV para sugerir márgenes, combos o detectar descuadres.

## Fases
1. **Capa 1:** Análisis de ventas diario -> Gemini cruza datos de clima/eventos y recomienda qué cantidad asar.
2. **Capa 2:** Cierre de Caja -> Gemini revisa anulaciones, compara totales y alerta si hay descuadres sospechosos.
3. **Capa 3:** Optimización -> Auditoría mensual de productos que generan pérdidas o cuellos de botella en cocina.
