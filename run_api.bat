@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
 echo [ERROR] Python environment belum ada. Jalankan setup_windows.bat dahulu.
 pause
 exit /b 1
)
echo Backend: http://127.0.0.1:8000/docs
echo Frontend dev dijalankan terpisah melalui run_frontend.bat
".venv\Scripts\python.exe" -m uvicorn api:app --host 127.0.0.1 --port 8000
pause
