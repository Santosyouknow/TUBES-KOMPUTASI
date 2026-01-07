#!/bin/bash
# Script untuk Todo App: Start Docker, Scaling, dan Load Test (Linux/Mac)

echo "========================================"
echo "    Todo App - Quick Start (Mac/Linux)"
echo "========================================"
echo

echo "Pilih opsi:"
echo "1. Start aplikasi (Docker Compose)"
echo "2. Scale services (horizontal scaling)"
echo "3. Jalankan load test"
echo "4. Exit"
echo "5. Stop semua container yang berjalan"
echo
read -p "Pilihan Anda (1-5): " choice

if [[ "$choice" == "1" ]]; then
    echo
    echo "🚀 Memulai Todo App dengan Docker Compose..."
    if docker compose version >/dev/null 2>&1; then
        COMPOSE_CMD="docker compose"
    else
        COMPOSE_CMD="docker-compose"
    fi
    $COMPOSE_CMD up -d
    if [[ $? -ne 0 ]]; then
        echo "❌ Error saat memulai aplikasi!"
        exit 1
    fi
    echo "✅ Aplikasi berhasil dijalankan!"
    exit 0
elif [[ "$choice" == "2" ]]; then
    echo
    echo "⚖️  Horizontal Scaling"
    if docker compose version >/dev/null 2>&1; then
        COMPOSE_CMD="docker compose"
    else
        COMPOSE_CMD="docker-compose"
    fi
    read -p "Jumlah API replicas (1-10, default 3): " api_replicas
    if [[ -z "$api_replicas" ]]; then api_replicas=3; fi
    echo "🔄 Scaling API services to $api_replicas replicas..."
    $COMPOSE_CMD up -d --scale api1=$api_replicas --scale api2=$api_replicas --scale api3=$api_replicas
    $COMPOSE_CMD ps
    echo "✅ Scaling completed!"
    exit 0
elif [[ "$choice" == "3" ]]; then
    echo
    echo "🧪 Load Testing Suite"
    echo "Pilih jenis test:"
    echo "1. Simple Load Test (5 users, 30 detik)"
    echo "2. Standard Load Test (10 users, 60 detik)"
    echo "3. Stress Test (hingga 50 users)"
    echo "4. Docker Container Monitoring Test"
    echo
    read -p "Pilihan test (1-4): " test_choice

    if ! command -v python3 >/dev/null 2>&1; then
        echo "❌ Python3 tidak ditemukan!"
        echo "Install Python 3.8+ untuk menjalankan load testing"
        exit 1
    fi

    python3 -c "import requests" 2>/dev/null
    if [[ $? -ne 0 ]]; then
        echo "📦 Installing Python dependencies..."
        pip3 install -r tests/requirements.txt
    fi

    if [[ "$test_choice" == "1" ]]; then
        echo "🚀 Running Simple Load Test..."
        (cd tests && python3 simple_load_test.py)
    elif [[ "$test_choice" == "2" ]]; then
        echo "🚀 Running Standard Load Test..."
        (cd tests && python3 load_test.py --users 10 --duration 60)
    elif [[ "$test_choice" == "3" ]]; then
        echo "🚀 Running Stress Test..."
        read -p "Continue? (y/n): " confirm
        if [[ "$confirm" == "y" || "$confirm" == "Y" ]]; then
            (cd tests && python3 stress_test.py --max-users 50 --ramp-up 180)
        fi
    elif [[ "$test_choice" == "4" ]]; then
        echo "🚀 Running Docker Monitoring Test..."
        (cd tests && python3 docker_load_test.py --users 8 --duration 45)
    else
        echo "Invalid choice!"
    fi
    exit 0
elif [[ "$choice" == "4" ]]; then
    echo
    echo "👋 Terima kasih telah menggunakan Todo App!"
    exit 0
elif [[ "$choice" == "5" ]]; then
    echo
    echo "🛑 Menghentikan dan menghapus seluruh container Docker yang berjalan..."
    running=$(docker ps -q)
    if [[ -z "$running" ]]; then
        echo "Tidak ada container yang sedang berjalan."
    else
        docker stop $running
        all=$(docker ps -aq)
        if [[ -n "$all" ]]; then
            docker rm $all
        fi
        echo "Semua container berhasil dihentikan dan dihapus."
    fi
    exit 0
else
    echo "Pilihan tidak valid!"
    exit 1
fi
