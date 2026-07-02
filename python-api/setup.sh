#!/bin/bash
# Instala el entorno virtual y las dependencias de la API Python
cd "$(dirname "$0")"

echo "→ Creando entorno virtual..."
python3 -m venv .venv

echo "→ Activando entorno virtual..."
source .venv/bin/activate

echo "→ Instalando dependencias..."
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

echo ""
echo "✅ Setup completado. Ya puedes usar 'npm run dev' para iniciar todo."
