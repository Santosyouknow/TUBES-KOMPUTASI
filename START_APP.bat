@echo off
REM Script untuk menjalankan Todo App dengan mudah (Updated 2026)

echo ========================================
echo     Todo App - Quick Start v2.0
echo ========================================
echo.

REM Cek apakah Docker berjalan
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Docker tidak ditemukan!
    echo.
    echo Silakan install Docker Desktop 4.0+ terlebih dahulu:
    echo https://www.docker.com/products/docker-desktop/
    echo.
    echo Minimum requirements:
    echo - RAM: 6GB+ allocated to Docker
    echo - CPU: 4+ cores
    echo - Storage: 5GB+ free space
    echo.
    pause
    exit /b 1
)

echo ✅ Docker terdeteksi
docker --version

REM Cek Docker Compose V2
docker compose version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Docker Compose V2 tidak ditemukan
    echo Menggunakan docker-compose legacy...
    set COMPOSE_CMD=docker-compose
) else (
    echo ✅ Docker Compose V2 detected
    set COMPOSE_CMD=docker compose
)

echo.

REM Cek apakah Docker daemon berjalan
docker info >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Docker Desktop belum berjalan
    echo.
    echo Silakan:
    echo 1. Buka Docker Desktop dari Start Menu
    echo 2. Tunggu sampai fully loaded (ikon whale hijau)
    echo 3. Pastikan allocated memory 6GB+ (Settings → Resources)
    echo 4. Jalankan script ini lagi
    echo.
    pause
    exit /b 1
)

echo ✅ Docker Desktop berjalan
echo.

REM Cek resource allocation
for /f "tokens=*" %%i in ('docker info ^| findstr "Total Memory"') do set DOCKER_MEMORY=%%i
echo Docker Memory: %DOCKER_MEMORY%
echo.

echo Pilih opsi:
echo 1. Start aplikasi (normal)
echo 2. Start aplikasi (fresh install - hapus data lama)
echo 3. Start aplikasi (development mode dengan hot reload)
echo 4. Stop aplikasi
echo 5. Lihat status aplikasi
echo 6. Lihat logs aplikasi (real-time)
echo 7. Monitor resource usage
echo 8. Scale services (horizontal scaling)
echo 9. Run load testing
echo 10. Reset aplikasi (hapus semua data)
echo 11. Health check & diagnostics
echo 12. Exit
echo.

set /p choice="Pilihan Anda (1-12): "

if "%choice%"=="1" goto start_normal
if "%choice%"=="2" goto start_fresh
if "%choice%"=="3" goto start_dev
if "%choice%"=="4" goto stop_app
if "%choice%"=="5" goto show_status
if "%choice%"=="6" goto show_logs
if "%choice%"=="7" goto monitor_resources
if "%choice%"=="8" goto scale_services
if "%choice%"=="9" goto run_load_test
if "%choice%"=="10" goto reset_app
if "%choice%"=="11" goto health_check
if "%choice%"=="12" goto exit_script

echo Pilihan tidak valid!
pause
goto :eof

:start_normal
echo.
echo 🚀 Memulai Todo App (Normal Mode)...
echo.
%COMPOSE_CMD% up -d

if errorlevel 1 (
    echo.
    echo ❌ Error saat memulai aplikasi!
    echo Coba gunakan opsi 2 (fresh install) atau 11 (diagnostics)
    pause
    goto :eof
)

echo.
echo ⏳ Menunggu aplikasi siap (60 detik)...
timeout /t 60 /nobreak >nul

call :test_application
goto :eof

:start_fresh
echo.
echo 🔄 Fresh install - menghapus data lama...
echo.
%COMPOSE_CMD% down -v --remove-orphans
docker system prune -f --volumes

echo.
echo 🚀 Memulai aplikasi dengan data bersih...
echo.
%COMPOSE_CMD% up -d --build --pull always

if errorlevel 1 (
    echo.
    echo ❌ Error saat memulai aplikasi!
    echo Cek logs dengan: %COMPOSE_CMD% logs
    pause
    goto :eof
)

echo.
echo ⏳ Menunggu aplikasi siap (90 detik untuk build)...
timeout /t 90 /nobreak >nul

echo.
echo 🗄️ Setup database...
call :setup_database

call :test_application
goto :eof

:start_dev
echo.
echo 🛠️ Starting Development Mode...
echo Features: Hot reload, debug logs, development tools
echo.

REM Check if dev compose file exists
if not exist "docker-compose.dev.yml" (
    echo ⚠️  docker-compose.dev.yml not found, using standard mode
    %COMPOSE_CMD% up -d --build
) else (
    %COMPOSE_CMD% -f docker-compose.yml -f docker-compose.dev.yml up -d --build
)

echo.
echo 📝 Development mode active:
echo - File watching enabled
echo - Debug logs enabled
echo - Hot reload active
echo.

call :test_application
goto :eof

:stop_app
echo.
echo 🛑 Menghentikan aplikasi...
echo.
docker-compose stop

echo.
echo ✅ Aplikasi berhasil dihentikan
echo.
echo 💡 Untuk menjalankan lagi: pilih opsi 1
echo 💡 Data masih tersimpan dan akan kembali saat restart
echo.
pause
goto :eof

:show_status
echo.
echo 📊 Status Aplikasi:
echo.
docker-compose ps

echo.
echo 📈 Resource Usage:
docker stats --no-stream

echo.
pause
goto :eof

:show_logs
echo.
echo 📋 Logs Aplikasi (tekan Ctrl+C untuk keluar):
echo.
docker-compose logs -f
goto :eof

:reset_app
echo.
echo ⚠️  PERINGATAN: Ini akan menghapus SEMUA data aplikasi!
set /p confirm="Yakin ingin reset? (y/n): "
if not /i "%confirm%"=="y" (
    echo Reset dibatalkan
    pause
    goto :eof
)

echo.
echo 🗑️ Menghapus semua data...
docker-compose down -v
docker system prune -f --volumes
docker image prune -f

echo.
echo ✅ Reset selesai!
echo 💡 Gunakan opsi 2 untuk start fresh
echo.
pause
goto :eof

:exit_script
echo.
echo 👋 Terima kasih telah menggunakan Todo App!
echo.
exit /b 0
:monitor_resources
echo.
echo 📊 Resource Monitoring (tekan Ctrl+C untuk keluar)
echo.
echo Container Resource Usage:
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
goto :eof

:scale_services
echo.
echo ⚖️ Horizontal Scaling
echo.
echo Current service status:
%COMPOSE_CMD% ps --format "table {{.Name}}\t{{.Status}}"
echo.
set /p api_replicas="Jumlah API replicas (1-10, default 3): "
if "%api_replicas%"=="" set api_replicas=3

echo.
echo 🔄 Scaling API services to %api_replicas% replicas...
%COMPOSE_CMD% up -d --scale api1=%api_replicas% --scale api2=%api_replicas% --scale api3=%api_replicas%

echo.
echo ✅ Scaling completed!
echo.
%COMPOSE_CMD% ps
pause
goto :eof

:run_load_test
echo.
echo 🧪 Load Testing Suite
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python tidak ditemukan!
    echo Install Python 3.8+ untuk menjalankan load testing
    pause
    goto :eof
)

echo ✅ Python detected
echo.

REM Check if requirements are installed
python -c "import requests" >nul 2>&1
if errorlevel 1 (
    echo 📦 Installing Python dependencies...
    pip install -r tests/requirements.txt
)

echo Pilih jenis test:
echo 1. Simple Load Test (5 users, 30 detik)
echo 2. Standard Load Test (10 users, 60 detik)
echo 3. Stress Test (hingga 50 users)
echo 4. Docker Container Monitoring Test
echo.

set /p test_choice="Pilihan test (1-4): "

if "%test_choice%"=="1" (
    echo.
    echo 🚀 Running Simple Load Test...
    cd tests
    python simple_load_test.py
    cd ..
) else if "%test_choice%"=="2" (
    echo.
    echo 🚀 Running Standard Load Test...
    cd tests
    python load_test.py --users 10 --duration 60
    cd ..
) else if "%test_choice%"=="3" (
    echo.
    echo 🚀 Running Stress Test...
    echo ⚠️  This will put high load on the system!
    set /p confirm="Continue? (y/n): "
    if /i "%confirm%"=="y" (
        cd tests
        python stress_test.py --max-users 50 --ramp-up 180
        cd ..
    )
) else if "%test_choice%"=="4" (
    echo.
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

:health_check
echo.
echo 🏥 Health Check & Diagnostics
echo.

echo 1. Container Status:
%COMPOSE_CMD% ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}\t{{.Health}}"

echo.
echo 2. Service Health Checks:
curl -s http://localhost/health && echo " ✅ API Health OK" || echo " ❌ API Health FAIL"
curl -s http://localhost:8080 >nul && echo "✅ Frontend OK" || echo "❌ Frontend FAIL"
curl -s http://localhost:5050 >nul && echo "✅ pgAdmin OK" || echo "❌ pgAdmin FAIL"

echo.
echo 3. Resource Usage:
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

echo.
echo 4. Network Connectivity:
%COMPOSE_CMD% exec api1 ping -c 1 postgres >nul && echo "✅ API → Database OK" || echo "❌ API → Database FAIL"
%COMPOSE_CMD% exec api1 ping -c 1 redis >nul && echo "✅ API → Redis OK" || echo "❌ API → Redis FAIL"

echo.
echo 5. Database Status:
%COMPOSE_CMD% exec postgres psql -U todouser -d tododb -c "SELECT COUNT(*) as todo_count FROM todos;" 2>nul && echo "✅ Database Query OK" || echo "❌ Database Query FAIL"

echo.
echo 6. Recent Errors (last 50 lines):
%COMPOSE_CMD% logs --tail=50 | findstr -i error

echo.
pause
goto :eof

:setup_database
REM Enhanced database setup with error handling
echo Setting up database tables and initial data...

REM Wait for postgres to be ready
:wait_postgres
%COMPOSE_CMD% exec postgres pg_isready -U todouser >nul 2>&1
if errorlevel 1 (
    echo Waiting for PostgreSQL to be ready...
    timeout /t 5 /nobreak >nul
    goto wait_postgres
)

REM Create tables
%COMPOSE_CMD% exec postgres psql -U todouser -d tododb -c "CREATE TABLE IF NOT EXISTS todos (id SERIAL PRIMARY KEY, title VARCHAR(255) NOT NULL, completed BOOLEAN DEFAULT FALSE, description TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);" >nul 2>&1

REM Insert sample data
%COMPOSE_CMD% exec postgres psql -U todouser -d tododb -c "INSERT INTO todos (title, completed, description) VALUES ('Learn Docker', false, 'Master containerization technology'), ('Build scalable API', true, 'Create REST API with Node.js'), ('Setup load balancing', false, 'Configure Nginx load balancer'), ('Add caching layer', true, 'Implement Redis caching'), ('Implement health checks', false, 'Add monitoring endpoints') ON CONFLICT DO NOTHING;" >nul 2>&1

echo ✅ Database setup completed
goto :eof

:test_application
echo.
echo 🧪 Testing aplikasi...

REM Test health endpoint
curl -s http://localhost/health >nul 2>&1
if not errorlevel 1 (
    echo ✅ Health check passed
) else (
    echo ❌ Health check failed
    echo Checking if services are still starting...
    timeout /t 30 /nobreak >nul
    curl -s http://localhost/health >nul 2>&1
    if not errorlevel 1 (
        echo ✅ Health check passed (after retry)
    ) else (
        echo ❌ Health check still failing - check logs
    )
)

REM Test API endpoint
curl -s http://localhost/todos >nul 2>&1
if not errorlevel 1 (
    echo ✅ API endpoint working
) else (
    echo ⚠️  API endpoint not responding
)

REM Test frontend
curl -s http://localhost:8080 >nul 2>&1
if not errorlevel 1 (
    echo ✅ Frontend accessible
) else (
    echo ⚠️  Frontend not accessible
)

echo.
echo ✅ Aplikasi berhasil dimulai!
echo.
echo 🌐 Akses aplikasi di:
echo   - 🌐 Frontend: http://localhost:8080
echo   - 🔌 API: http://localhost/todos
echo   - 🗄️ pgAdmin: http://localhost:5050 (admin@example.com / admin123)
echo   - ❤️ Health: http://localhost/health
echo.
echo 📊 Commands:
echo   - Status: %COMPOSE_CMD% ps
echo   - Logs: %COMPOSE_CMD% logs -f
echo   - Stats: docker stats
echo.

set /p open="Buka aplikasi di browser? (y/n): "
if /i "%open%"=="y" (
    start http://localhost:8080
)

pause
goto :eof