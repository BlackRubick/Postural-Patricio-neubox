# Arranca la API Python en puerto 8000
Set-Location $PSScriptRoot

if (-Not (Test-Path ".venv")) {
    Write-Host "-> Entorno virtual no encontrado. Instalando dependencias..."

    # Usar Python 3.11 explicitamente (compatible con mediapipe)
    $pythonCmd = $null
    if (Get-Command "py" -ErrorAction SilentlyContinue) {
        try { py -3.11 --version 2>$null | Out-Null; $pythonCmd = "py -3.11" } catch {}
        if (-Not $pythonCmd) {
            try { py -3.10 --version 2>$null | Out-Null; $pythonCmd = "py -3.10" } catch {}
        }
    }
    if (-Not $pythonCmd) {
        $pythonCmd = "python"
    }

    Write-Host "-> Usando: $pythonCmd"
    Invoke-Expression "$pythonCmd -m venv .venv"

    if (-Not (Test-Path ".venv\Scripts\python.exe")) {
        Write-Host "ERROR: No se pudo crear el entorno virtual."
        exit 1
    }

    Write-Host "-> Actualizando pip..."
    & .\.venv\Scripts\python.exe -m pip install --upgrade pip

    Write-Host "-> Instalando dependencias..."
    & .\.venv\Scripts\python.exe -m pip install -r requirements.txt

    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Fallo la instalacion de dependencias."
        exit 1
    }

    Write-Host "-> Instalacion completada."
}

& .\.venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
