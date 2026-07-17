# Instala el entorno virtual y las dependencias de la API Python
Set-Location $PSScriptRoot

Write-Host "-> Creando entorno virtual..."
python -m venv .venv

Write-Host "-> Instalando dependencias..."
.\.venv\Scripts\python.exe -m pip install --upgrade pip --quiet
.\.venv\Scripts\python.exe -m pip install -r requirements.txt --quiet

Write-Host ""
Write-Host "Setup completado. Ya puedes usar 'npm run dev' para iniciar todo."
