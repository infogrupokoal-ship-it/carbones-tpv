# Política de Control de Costes Gemini

Dado el uso de una cuenta Gemini Premium (aprox 250€/mes), la estrategia es maximizar su uso sin derrochar cuotas o llegar a rate-limits.

## Recomendación de Modelos por Tarea

1. **Gemini 1.5 Flash (Rápido y Barato):**
   - Agente Tester, Agente Documentador, flujos de WhatsApp simples y categorización.
2. **Gemini 1.5 Pro / Advanced (Razonamiento Profundo):**
   - Agente Arquitecto, Agente Revisor de Código, Agente Auditor Final.
3. **Gemini 1.5 Pro Vision:**
   - Para revisar facturas, fotos de averías en Grupo Koal o recibos en Carbones TPV.

## Control de Limites

- En código, usar la variable `GEMINI_DAILY_CALL_LIMIT` (ej. 5000) y abortar/alertar si se supera.
- Habilitar `GEMINI_ENABLE_COST_GUARD=1` para impedir enviar payloads masivos (ej. base de datos entera) sin una condensación previa.

> [!TIP]
> Antes de subir un archivo enorme a Gemini, usar un script local básico (o un modelo menor) para resumir o extraer solo las líneas relevantes.
