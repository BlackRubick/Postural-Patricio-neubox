#!/bin/bash
# Arranca la API Python en puerto 8000
cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
  echo "⚠️  Entorno virtual no encontrado. Ejecuta primero: bash python-api/setup.sh"
  exit 1
fi

# Windows usa Scripts/activate, Linux/Mac usa bin/activate
if [ -f ".venv/Scripts/activate" ]; then
  source .venv/Scripts/activate
else
  source .venv/bin/activate
fi

exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload
