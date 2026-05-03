# Proveedores IA y Fallbacks

Este proyecto utiliza una arquitectura Multi-Agente IA. A continuación se define la jerarquía de los proveedores.

## 1. Proveedor Principal: Gemini Advanced (Pro Tier)
- **Costo:** Pagado en tarifa plana (250€/mes).
- **Rol:** IA Arquitecta, IA Revisora y IA Principal.
- **Ventaja:** Ventana de contexto masiva. Se le debe enviar el código completo y los logs enteros sin filtrar.

## 2. Proveedor Secundario / Fallback (Opcional): OpenRouter
- **Costo:** Pago por uso (Créditos).
- **Rol:** Solo se usará si Gemini falla por un outage global. Modelos: Claude 3.5 Sonnet o GPT-4o.
- **Config:** Requiere `OPENROUTER_API_KEY` en el `.env`.

## 3. Proveedor Local de Emergencia: Ollama
- **Costo:** Gratis.
- **Rol:** Tareas sencillas, IA de Seguridad local para revisar datos PII que no deban enviarse a la nube.
- **Config:** Apuntar base URL a `http://localhost:11434`.

> [!CAUTION]
> No almacenar API KEYS reales en este repositorio ni hacer commit de ellas.
