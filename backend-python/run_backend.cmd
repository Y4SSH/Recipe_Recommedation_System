@echo off
setlocal

set SCRIPT_DIR=%~dp0
for %%I in ("%SCRIPT_DIR%..") do set REPO_ROOT=%%~fI

set PYTHON_EXE=%REPO_ROOT%\.venv\Scripts\python.exe
if not exist "%PYTHON_EXE%" set PYTHON_EXE=%SCRIPT_DIR%venv\Scripts\python.exe

if not exist "%PYTHON_EXE%" (
  echo Python virtual environment not found. Expected .venv or backend-python\venv.
  exit /b 1
)

set PORT=8001
if not "%~1"=="" set PORT=%~1

cd /d "%SCRIPT_DIR%"
echo Starting backend on port %PORT% using %PYTHON_EXE%
"%PYTHON_EXE%" -m uvicorn app.main:app --host 0.0.0.0 --port %PORT%

endlocal
