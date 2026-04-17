param(
    [int]$Port = 8001
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptDir

$venvPythonRoot = Join-Path $repoRoot ".venv\Scripts\python.exe"
$venvPythonLocal = Join-Path $scriptDir "venv\Scripts\python.exe"

if (Test-Path $venvPythonRoot) {
    $pythonExe = $venvPythonRoot
} elseif (Test-Path $venvPythonLocal) {
    $pythonExe = $venvPythonLocal
} else {
    Write-Error "Python virtual environment not found. Expected .venv or backend-python\\venv."
    exit 1
}

Set-Location $scriptDir
Write-Host "Starting backend on port $Port using $pythonExe"
& $pythonExe -m uvicorn app.main:app --host 0.0.0.0 --port $Port
