# Arranca la API Python en puerto 8000
Set-Location $PSScriptRoot

if (-Not (Test-Path ".venv")) {
    Write-Host "-> Entorno virtual no encontrado. Instalando dependencias..."
    python -m venv .venv
    .\.venv\Scripts\python.exe -m pip install --upgrade pip --quiet
    .\.venv\Scripts\python.exe -m pip install -r requirements.txt --quiet
    Write-Host "-> Instalación completada."
}

& .\.venv\Scripts\uvicorn.exe main:app --host 0.0.0.0 --port 8000 --reload
