@echo off
setlocal enabledelayedexpansion
REM Script untuk menjalankan Todo App: Start Docker, Scaling, dan Load Test

echo ========================================
echo     Todo App - Quick Start
echo ========================================
echo.

echo Pilih opsi:
echo 1. Start aplikasi (Docker Compose)
echo 2. Scale services (horizontal scaling)
echo 3. Jalankan load test
echo 4. Exit
echo 5. Stop dan hapus semua container yang berjalan
echo.
set /p choice="Pilihan Anda (1-5): "

REM Pilihan 1: Start aplikasi
echo.
if "%choice%"=="1" goto start_app
if "%choice%"=="2" goto scale_services
if "%choice%"=="3" goto run_load_test
if "%choice%"=="4" goto exit_script
if "%choice%"=="5" goto stop_and_remove_all_containers

echo Pilihan tidak valid!
pause
goto :eof

:start_app
echo.
echo 🚀 Memulai Todo App dengan Docker Compose...
echo.
docker compose version >nul 2>&1
if %errorlevel% neq 0 (
    set "COMPOSE_CMD=docker-compose"
) else (
    set "COMPOSE_CMD=docker compose"
)
%COMPOSE_CMD% up -d
if %errorlevel% neq 0 (
    echo ❌ Error saat memulai aplikasi!
    pause
    goto :eof
)
echo ✅ Aplikasi berhasil dijalankan!
echo.
pause
goto :eof

:scale_services
echo.
echo ⚖️  Horizontal Scaling

docker compose version >nul 2>&1
if %errorlevel% neq 0 (
    set "COMPOSE_CMD=docker-compose"
) else (
    set "COMPOSE_CMD=docker compose"
)
echo.
set /p api_replicas="Jumlah API replicas (1-10, default 3): "
if "%api_replicas%"=="" set api_replicas=3
echo 🔄 Scaling API services to %api_replicas% replicas...
%COMPOSE_CMD% up -d --scale api1=%api_replicas% --scale api2=%api_replicas% --scale api3=%api_replicas%
echo.
%COMPOSE_CMD% ps
echo ✅ Scaling completed!
pause
goto :eof

:run_load_test
echo.
echo 🧪 Load Testing Suite

echo Pilih jenis test:
echo 1. Simple Load Test (5 users, 30 detik)
echo 2. Standard Load Test (10 users, 60 detik)
echo 3. Stress Test (hingga 50 users)
echo 4. Docker Container Monitoring Test
echo.
set /p test_choice="Pilihan test (1-4): "

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python tidak ditemukan!
    echo Install Python 3.8+ untuk menjalankan load testing
    pause
    goto :eof
)

REM Check if requirements are installed
python -c "import requests" >nul 2>&1
if %errorlevel% neq 0 (
    echo 📦 Installing Python dependencies...
    pip install -r tests/requirements.txt
)

if "%test_choice%"=="1" (
    echo 🚀 Running Simple Load Test...
    cd tests
    python simple_load_test.py
    cd ..
) else if "%test_choice%"=="2" (
    echo 🚀 Running Standard Load Test...
    cd tests
    python load_test.py --users 10 --duration 60
    cd ..
) else if "%test_choice%"=="3" (
    echo 🚀 Running Stress Test...
    set /p confirm="Continue? (y/n): "
    if /i "%confirm%"=="y" (
        cd tests
        python stress_test.py --max-users 50 --ramp-up 180
        cd ..
    )
) else if "%test_choice%"=="4" (
    echo 🚀 Running Docker Monitoring Test...
    cd tests
    python docker_load_test.py --users 8 --duration 45
    cd ..
) else (
    echo Invalid choice!
)
echo.
pause
goto :eof

:stop_and_remove_all_containers
echo.
echo 🛑 Menghentikan dan menghapus seluruh container Docker yang berjalan...
for /f %%i in ('docker ps -q') do docker stop %%i
for /f %%i in ('docker ps -aq') do docker rm %%i
echo Semua container berhasil dihentikan dan dihapus.
pause
goto :eof

:exit_script
echo.
echo 👋 Terima kasih telah menggunakan Todo App!
echo.
endlocal
exit /b 0