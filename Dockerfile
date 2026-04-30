# 🐳 Dockerfile Enterprise - Carbones y Pollos TPV
# Optimizado para rendimiento y seguridad (Multi-stage build)

FROM python:3.10-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --user --no-cache-dir -r requirements.txt

FROM python:3.10-slim as runner

WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .

ENV PATH=/root/.local/bin:$PATH
ENV DATABASE_URL=sqlite:////data/tpv_data.sqlite
ENV PYTHONUNBUFFERED=1

# Puerto de exposición
EXPOSE 8000

# Punto de montaje para persistencia
VOLUME ["/data"]

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
