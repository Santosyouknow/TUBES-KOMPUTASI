@echo off
REM Script untuk menjalankan load testing pada Windows

echo ========================================
echo Todo App Load Testing Suite
echo ========================================
echo.

REM Cek apakah Python terinstall
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python tidak ditemukan!
    echo Silakan install Python terlebih dahulu.
    pause
    exit /b 1
)

REM Install dependencies jika belum ada
echo Installing Python dependencies...
pip install -r requirements.txt

echo.
echo Pilih jenis test yang ingin dijalankan:
echo 1. Simple Load Test (5 users, 30 detik)
echo 2. Load Test (10 users, 60 detik)
echo 3. Stress Test (hingga 100 users)
echo 4. Custom Load Test
echo 5. Exit
echo.

set /p choice="Pilihan Anda (1-5): "

if "%choice%"=="1" (
    echo.
    echo Menjalankan Simple Load Test...
    python simple_load_test.py
) else if "%choice%"=="2" (
    echo.
    echo Menjalankan Load Test...
    python load_test.py --users 10 --duration 60
) else if "%choice%"=="3" (
    echo.
    echo Menjalankan Stress Test...
    echo PERINGATAN: Test ini akan memberikan beban tinggi pada sistem!
    set /p confirm="Lanjutkan? (y/n): "
    if /i "%confirm%"=="y" (
        python stress_test.py --max-users 100 --ramp-up 300
    ) else (
        echo Test dibatalkan.
    )
) else if "%choice%"=="4" (
    echo.
    echo Custom Load Test
    set /p users="Jumlah users: "
    set /p duration="Durasi (detik): "
    set /p url="URL (default http://localhost): "
    if "%url%"=="" set url=http://localhost
    
    python load_test.py --users %users% --duration %duration% --url %url% --save
) else if "%choice%"=="5" (
    echo Keluar...
    exit /b 0
) else (
    echo Pilihan tidak valid!
    pause
    goto :eof
)

echo.
echo Test selesai!
pause