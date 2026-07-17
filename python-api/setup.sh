#!/bin/bash
# Instala el entorno virtual y las dependencias de la API Python
cd "$(dirname "$0")"

echo "→ Creando entorno virtual..."
# En Windows 'python3' puede no existir, usar 'python' como fallback
PYTHON=$(command -v python3 2>/dev/null || command -v python 2>/dev/null)
"$PYTHON" -m venv .venv

echo "→ Activando entorno virtual..."
# Windows usa Scripts/activate, Linux/Mac usa bin/activate
if [ -f ".venv/Scripts/activate" ]; then
  source .venv/Scripts/activate
else
  source .venv/bin/activate
fi

echo "→ Instalando dependencias..."
python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt --quiet

echo ""
echo "✅ Setup completado. Ya puedes usar 'npm run dev' para iniciar todo."