# Arranca la API Python en puerto 8000
Set-Location $PSScriptRoot

if (-Not (Test-Path ".venv")) {
    Write-Host "-> Entorno virtual no encontrado. Instalando dependencias..."
    python -m venv .venv
    if (-Not (Test-Path ".venv")) {
        Write-Host "ERROR: No se pudo crear el entorno virtual. Asegurate de tener Python instalado."
        exit 1
    }
    .\.venv\Scripts\python.exe -m pip install --upgrade pip
    .\.venv\Scripts\python.exe -m pip install -r requirements.txt
    Write-Host "-> Instalacion completada."
}

& .\.venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
