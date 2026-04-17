@echo off
setlocal

set SCRIPT_DIR=%~dp0

if /I "%~1"=="rollback" (
  powershell -ExecutionPolicy Bypass -File "%SCRIPT_DIR%switch_dataset.ps1" -Rollback
  exit /b %ERRORLEVEL%
)

set CSV_PATH=..\recipes_extended.csv
if not "%~1"=="" set CSV_PATH=%~1

set BATCH_SIZE=2000
if not "%~2"=="" set BATCH_SIZE=%~2

powershell -ExecutionPolicy Bypass -File "%SCRIPT_DIR%switch_dataset.ps1" -CsvPath "%CSV_PATH%" -BatchSize %BATCH_SIZE%

endlocal
