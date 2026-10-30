#!/usr/bin/env bash
# ==============================================================================
# Script de aprovisionamiento para Amazon EC2 (Ubuntu 22.04 / 24.04 LTS)
# Configura el entorno Python, clona/actualiza dependencias y activa el servicio systemd
# ==============================================================================

set -euo pipefail

echo "==> [1/6] Actualizando paquetes del sistema..."
sudo apt update -y
sudo apt upgrade -y

echo "==> [2/6] Instalando dependencias de Python y Git..."
sudo apt install -y python3-pip python3-venv git curl

APP_DIR="/home/ubuntu/aws-url-shortener"
BACKEND_DIR="${APP_DIR}/backend"

# Si el repositorio no existe en /home/ubuntu, informar o clonar
if [ ! -d "${BACKEND_DIR}" ]; then
  echo "Asegúrate de clonar el repositorio en /home/ubuntu/aws-url-shortener"
  echo "Ejemplo: git clone <URL-DEL-REPO> ${APP_DIR}"
  exit 1
fi

echo "==> [3/6] Configurando entorno virtual de Python..."
cd "${BACKEND_DIR}"
if [ ! -d "venv" ]; then
  python3 -m venv venv
fi

# Activar e instalar requerimientos
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "==> [4/6] Verificando archivo de entorno (.env)..."
if [ ! -f ".env" ]; then
  if [ -f "../.env.example" ]; then
    cp ../.env.example .env
    echo "Se ha creado un .env de ejemplo. Por favor edítalo con la IP y región correctas."
  fi
fi

echo "==> [5/6] Instalando servicio de systemd..."
sudo cp urlshortener.service /etc/systemd/system/urlshortener.service
sudo systemctl daemon-reload
sudo systemctl enable urlshortener
sudo systemctl restart urlshortener

echo "==> [6/6] Verificando estado del servicio..."
sudo systemctl status urlshortener --no-pager

echo "=============================================================================="
echo "¡Despliegue de Backend completado exitosamente!"
echo "Prueba tu API ejecutando: curl http://localhost:8000/health"
echo "=============================================================================="
