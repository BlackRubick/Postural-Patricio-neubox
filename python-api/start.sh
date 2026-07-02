#!/bin/bash
# Arranca la API Python en puerto 8000
cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
  echo "⚠️  Entorno virtual no encontrado. Ejecuta primero: bash python-api/setup.sh"
  exit 1
fi

source .venv/bin/activate
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload
