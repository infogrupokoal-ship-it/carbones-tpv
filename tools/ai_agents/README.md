# Orquestador Local de Agentes

Esta carpeta contiene los scripts para automatizar la ejecución de las IAs.
Dado que usamos Gemini Advanced, la mayoría de estas rondas pueden pedirse en un solo prompt (ej. "Actúa como Consejo de IAs y revisa esto").
Sin embargo, estos scripts sirven para iterar usando llamadas API (Gemini API, Ollama, OpenRouter) si se desea automatización total.

## Uso

```bash
python run_agent_cycle.py --project .
python agent_debate.py
```
