# Arranca la API Python en puerto 8000
Set-Location $PSScriptRoot

if (-Not (Test-Path ".venv")) {
    Write-Host "Entorno virtual no encontrado. Ejecuta primero: npm run setup:python"
    exit 1
}

& .\.venv\Scripts\uvicorn.exe main:app --host 0.0.0.0 --port 8000 --reload
