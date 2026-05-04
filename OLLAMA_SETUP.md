# Guía de Configuración Local de Ollama (Costo Cero)

Ollama permite ejecutar modelos LLM locales de forma gratuita, ideal como backup cuando Gemini no esté disponible o para tareas que no requieran máxima capacidad cognitiva.

## Requisitos

- RAM: Mínimo 8GB (recomendado 16GB+ para modelos de 8B parámetros).
- Instalación: [Ollama.com](https://ollama.com/)

## Instalación en Windows

1. Descargar el instalador de Windows.
2. Siguiente -> Siguiente -> Finalizar.
3. Abrir la terminal y ejecutar: `ollama run qwen2.5-coder` (Modelo ideal para código).

## Modelos Recomendados

- `llama3.1` (Uso general y chat)
- `qwen2.5-coder` (Mejor modelo local pequeño para código)
- `phi3` (Si tienes muy poca RAM)

> [!WARNING]
> No arranques modelos pesados en producción (VPS) sin comprobar antes el uso de memoria (`htop` o Task Manager) para no tumbar la base de datos o la app principal.
