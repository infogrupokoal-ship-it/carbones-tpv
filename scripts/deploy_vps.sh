#!/bin/bash
# 🚀 Carbones y Pollos TPV - VPS Deployment Script v2.0
# Este script automatiza el despliegue profesional usando Docker Compose.

echo "🍗 Iniciando despliegue Enterprise en VPS..."

# 1. Verificar dependencias
if ! [ -x "$(command -v docker-compose)" ]; then
  echo "❌ Error: docker-compose no está instalado." >&2
  exit 1
fi

# 2. Pull de la última versión
echo "📥 Sincronizando repositorio..."
git pull origin main

# 3. Preparar entorno
if [ ! -f .env ]; then
    echo "⚠️ Archivo .env no encontrado. Creando plantilla..."
    echo "DATABASE_URL=sqlite:////data/tpv_data.sqlite" >> .env
    echo "SECRET_KEY=$(openssl rand -hex 32)" >> .env
    echo "GEMINI_API_KEY=pon_tu_clave_aqui" >> .env
fi

# 4. Construir y levantar
echo "🏗️ Construyendo contenedores..."
docker-compose up -d --build

# 5. Limpieza
echo "🧹 Limpiando imágenes obsoletas..."
docker image prune -f

echo "✅ Despliegue completado con éxito."
echo "🌐 Acceso: http://tu-ip-o-dominio:8000"
echo "📊 Salud: http://tu-ip-o-dominio:8000/health"
