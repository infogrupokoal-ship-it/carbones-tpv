# 🐳 Dockerfile Enterprise v5.0 - Carbones y Pollos TPV
# Arquitectura Multi-stage optimizada para seguridad y despliegue rápido en Render

# --- Fase 1: Build & Dependencies ---
FROM python:3.12-slim as builder

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalar dependencias de sistema mínimas para compilación si fuera necesario
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt

# --- Fase 2: Final Runtime ---
FROM python:3.12-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1
ENV DATABASE_URL=sqlite:////data/tpv_data.sqlite
ENV TZ=Europe/Madrid

# Crear usuario no-root para seguridad industrial
RUN groupadd -r tpvuser && useradd -r -g tpvuser tpvuser && \
    mkdir -p instance logs static /data/backups && \
    chown -R tpvuser:tpvuser instance logs static /data && \
    chmod -R 755 instance logs static /data

# Copiar dependencias instaladas desde la fase builder
COPY --from=builder /install /usr/local
COPY . .

# Asegurar permisos correctos
RUN chown -R tpvuser:tpvuser /app

USER tpvuser

# Puerto operativo
EXPOSE 8000

# Persistencia de datos
VOLUME ["/data"]

# Healthcheck industrial
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/telemetry/healthz || exit 1

# Comando de arranque con optimizaciones de rendimiento
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4", "--proxy-headers"]
