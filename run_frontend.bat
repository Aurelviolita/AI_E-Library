@echo off
cd /d "%~dp0frontend"
if not exist "package.json" (
 echo [ERROR] File frontend/package.json tidak ditemukan.
 pause
 exit /b 1
)
if not exist "node_modules\.bin\vite.cmd" (
 echo Menyiapkan dependensi frontend...
 call npm.cmd install --no-audit --no-fund
 if errorlevel 1 (echo [ERROR] npm install gagal.& pause & exit /b 1)
)
echo Frontend: biasanya http://localhost:5173
call npm.cmd run dev
pause
