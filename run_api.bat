@echo off
chcp 65001 > nul
echo =========================================================================
echo   BPJS KESEHATAN - AI e-LIBRARY RECOMMENDATION REST API SERVICE
echo =========================================================================
echo.
echo Menjalankan backend server pada http://localhost:8000 ...
echo Dokumentasi Swagger UI : http://localhost:8000/docs
echo Dokumentasi ReDoc      : http://localhost:8000/redoc
echo Dashboard Interaktif   : http://localhost:8000/
echo.
echo Tekan CTRL+C untuk menghentikan server.
echo =========================================================================
echo.

cd /d "%~dp0"

:: 1. Cek dan bangun frontend jika belum ada
if not exist "frontend\dist\index.html" (
    echo [*] Membangun frontend dasbor...
    call npm.cmd --prefix frontend ci
    if errorlevel 1 exit /b 1
    call npm.cmd --prefix frontend run build
    if errorlevel 1 exit /b 1
)

:: 2. Jalankan backend server
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -m uvicorn api:app --host 0.0.0.0 --port 8000
) else (
    echo [*] Menjalankan server menggunakan Python sistem...
    python -m uvicorn api:app --host 0.0.0.0 --port 8000
    if errorlevel 1 (
        echo.
        echo [!] Gagal menjalankan uvicorn. Mencoba menginstal requirements.txt...
        python -m pip install -r requirements.txt
        python -m uvicorn api:app --host 0.0.0.0 --port 8000
    )
)

pause
