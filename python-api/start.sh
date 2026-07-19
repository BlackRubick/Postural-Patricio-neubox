#!/bin/bash
# Arranca la API Python en puerto 8000
cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
  echo "-> Entorno virtual no encontrado. Instalando dependencias..."
  python3 -m venv .venv
  .venv/bin/python -m pip install --upgrade pip --quiet
  .venv/bin/python -m pip install -r requirements.txt --quiet
  echo "-> Instalación completada."
fi

# Windows usa Scripts/activate, Linux/Mac usa bin/activate
if [ -f ".venv/Scripts/activate" ]; then
  source .venv/Scripts/activate
else
  source .venv/bin/activate
fi

exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload
