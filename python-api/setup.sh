#!/bin/bash
# Instala el entorno virtual y las dependencias de la API Python
cd "$(dirname "$0")"

echo "→ Creando entorno virtual..."
PYTHON=$(command -v python3 2>/dev/null || command -v python 2>/dev/null)

if [ -z "$PYTHON" ]; then
  echo "❌ Python no encontrado. Instálalo desde https://www.python.org/downloads/"
  echo "   Asegúrate de marcar 'Add Python to PATH' durante la instalación."
  exit 1
fi

# Verificar que no sea el alias vacío de Microsoft Store
if ! "$PYTHON" --version &>/dev/null; then
  echo "❌ Python no funciona correctamente. Instálalo desde https://www.python.org/downloads/"
  echo "   Asegúrate de marcar 'Add Python to PATH' durante la instalación."
  exit 1
fi

echo "   Usando: $($PYTHON --version) en $PYTHON"
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