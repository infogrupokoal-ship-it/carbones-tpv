# Auditoría de Integración Gemini

## Estado Actual

- **Grupo Koal:** No se detectan integraciones directas con `google.generativeai` en el código base.
- **Carbones TPV:** Se detecta uso activo de Gemini en:
  - `backend/utils/ai_model_manager.py`
  - `backend/services/ai_bi_agent.py`
  - `scripts/ai_engine.py`

## Riesgos y Consideraciones

- En Carbones TPV, la integración existente no debe ser modificada sin pruebas exhaustivas.
- La nueva capa Multi-Agente (`backend/ai/`) se construye de forma paralela y aislada para evitar regresiones en los servicios en producción.
- No hay evidencia de uso de variables estandarizadas para el control estricto de costes o partición clara de roles multi-agente en el código legacy.
