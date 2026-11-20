@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Membuat virtual environment...
  py -3.12 -m venv .venv
  if errorlevel 1 (
    echo Python 3.12 tidak ditemukan, mencoba Python default...
    py -m venv .venv
  )
  if errorlevel 1 (echo [ERROR] Pembuatan venv gagal. & pause & exit /b 1)
)
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (echo [ERROR] Instalasi gagal.& pause & exit /b 1)
echo [OK] Siap untuk run_api.bat dan run_frontend.bat
pause
