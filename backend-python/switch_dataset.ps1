param(
    [string]$CsvPath = "../recipes_extended.csv",
    [int]$BatchSize = 2000,
    [switch]$Rollback
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

$currentDb = Join-Path $scriptDir "recipes.db"
$tempDb = Join-Path $scriptDir "recipes.swap.db"
$rollbackDb = Join-Path $scriptDir "recipes.rollback.db"
$backupDir = Join-Path $scriptDir "db_backups"
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null

if ($Rollback) {
    if (-not (Test-Path $rollbackDb)) {
        Write-Error "Rollback DB not found at $rollbackDb"
        exit 1
    }

    if (Test-Path $currentDb) {
        $failedName = "recipes.failed-" + (Get-Date -Format "yyyyMMdd-HHmmss") + ".db"
        Move-Item -Path $currentDb -Destination (Join-Path $backupDir $failedName) -Force
    }

    Move-Item -Path $rollbackDb -Destination $currentDb -Force
    Write-Host "Rollback completed. Active DB restored from recipes.rollback.db"
    exit 0
}

$resolvedCsv = Resolve-Path -Path $CsvPath -ErrorAction SilentlyContinue
if (-not $resolvedCsv) {
    Write-Error "CSV file not found: $CsvPath"
    exit 1
}

if (Test-Path $tempDb) {
    Remove-Item $tempDb -Force
}

$env:DATABASE_URL = "sqlite:///./recipes.swap.db"

Write-Host "Importing into temporary DB using $pythonExe"
& $pythonExe import_data.py --csv "$($resolvedCsv.Path)" --batch-size $BatchSize
$importExitCode = $LASTEXITCODE

Remove-Item Env:DATABASE_URL -ErrorAction SilentlyContinue

if ($importExitCode -ne 0) {
    if (Test-Path $tempDb) {
        Remove-Item $tempDb -Force
    }
    Write-Error "Dataset import failed. Active recipes.db was not changed."
    exit $importExitCode
}

if (Test-Path $currentDb) {
    Write-Host "Preserving user accounts from current DB..."
    @'
import sqlite3

src = sqlite3.connect("recipes.db")
dst = sqlite3.connect("recipes.swap.db")
rows = src.execute(
    "SELECT id, name, email, password_hash, preferences, created_at, updated_at FROM users"
).fetchall()
dst.executemany(
    "INSERT OR IGNORE INTO users (id, name, email, password_hash, preferences, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
    rows,
)
dst.commit()
src.close()
dst.close()
print(f"Preserved users: {len(rows)}")
'@ | Set-Content -Path (Join-Path $scriptDir "_preserve_users_temp.py")

    & $pythonExe (Join-Path $scriptDir "_preserve_users_temp.py")
    $preserveExitCode = $LASTEXITCODE
    Remove-Item (Join-Path $scriptDir "_preserve_users_temp.py") -Force -ErrorAction SilentlyContinue

    if ($preserveExitCode -ne 0) {
        if (Test-Path $tempDb) {
            Remove-Item $tempDb -Force
        }
        Write-Error "Failed while preserving users. Active recipes.db was not changed."
        exit $preserveExitCode
    }

    $backupName = "recipes.before-swap-" + (Get-Date -Format "yyyyMMdd-HHmmss") + ".db"
    Copy-Item -Path $currentDb -Destination (Join-Path $backupDir $backupName) -Force

    if (Test-Path $rollbackDb) {
        Remove-Item $rollbackDb -Force
    }

    Move-Item -Path $currentDb -Destination $rollbackDb -Force
}

Move-Item -Path $tempDb -Destination $currentDb -Force

Write-Host "Dataset swap completed successfully."
Write-Host "One-click rollback available via: .\\switch_dataset.ps1 -Rollback"
