# 🚀 Cara Menjalankan Program Todo App (Updated 2026)

## 📋 Persyaratan Sistem

### Software yang Diperlukan:
1. **Docker Desktop 4.0+** - [Download di sini](https://www.docker.com/products/docker-desktop/)
2. **Git** (opsional) - untuk clone repository
3. **Python 3.8+** (opsional) - untuk load testing dan monitoring
4. **Web Browser** - Chrome, Firefox, Edge, atau Safari

### Spesifikasi Minimum:
- **RAM**: 6GB (Recommended: 12GB+ untuk load testing)
- **CPU**: 4 cores (Recommended: 8+ cores)
- **Storage**: 5GB free space
- **OS**: Windows 10/11 (build 19041+), macOS 10.15+, atau Linux Ubuntu 18.04+
- **Network**: Internet connection untuk download images

## 🔧 Langkah-langkah Instalasi

### Step 1: Install Docker Desktop (Terbaru)

1. **Download Docker Desktop**
   - Windows: https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe
   - macOS (Intel): https://desktop.docker.com/mac/main/amd64/Docker.dmg
   - macOS (Apple Silicon): https://desktop.docker.com/mac/main/arm64/Docker.dmg

2. **Install dengan pengaturan optimal**
   - ✅ Enable WSL 2 integration (Windows)
   - ✅ Enable Kubernetes (opsional)
   - ✅ Enable Docker Compose V2
   - ✅ Allocate minimal 4GB RAM untuk Docker

3. **Konfigurasi Docker Desktop**
   ```
   Settings → Resources → Advanced:
   - CPUs: 4+ cores
   - Memory: 6GB+ 
   - Swap: 2GB
   - Disk image size: 64GB+
   ```

### Step 2: Verifikasi Instalasi Docker

Buka Terminal/Command Prompt dan jalankan:

```bash
# Cek versi Docker
docker --version
# Output: Docker version 24.0.0+

# Cek Docker Compose
docker compose version
# Output: Docker Compose version v2.20.0+

# Test Docker berjalan
docker run hello-world
# Harus berhasil tanpa error
```

### Step 3: Clone atau Download Project

```bash
# Opsi 1: Clone dengan Git
git clone <repository-url>
cd todo-app

# Opsi 2: Download ZIP dan extract
# Lalu navigate ke folder project
cd path/to/todo-app
```

## 🚀 Cara Menjalankan Aplikasi

### Metode 1: Quick Start dengan Script Otomatis (Recommended)

**Windows:**
```cmd
# Double-click atau jalankan di Command Prompt
START_APP.bat
```

**macOS/Linux:**
```bash
# Buat executable dan jalankan
chmod +x start_app.sh
./start_app.sh
```

### Metode 2: Docker Compose Modern (Manual)

```bash
# 1. Pastikan di folder project
pwd  # Harus di folder yang ada docker-compose.yml

# 2. Build dan jalankan (first time)
docker compose up -d --build

# 3. Atau jalankan tanpa build (subsequent runs)
docker compose up -d

# 4. Verifikasi semua services berjalan
docker compose ps
```

### Metode 3: Development Mode (Hot Reload)

```bash
# Untuk development dengan auto-reload
docker compose -f docker-compose.yml -f docker-compose.dev.yml up

# Atau background mode
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

### Metode 4: Production Mode

```bash
# Set environment untuk production
export NODE_ENV=production
export COMPOSE_PROJECT_NAME=todo-app-prod

# Jalankan dengan production config
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## 🌐 Mengakses Aplikasi

Setelah aplikasi berjalan (tunggu 2-3 menit untuk startup), akses melalui:

### Aplikasi Utama:
- **🌐 Frontend (Web App)**: http://localhost:8080
  - Interface utama untuk pengguna
  - Responsive design untuk mobile & desktop
  - Real-time updates

- **🔌 API Endpoints**: http://localhost/api/
  - REST API dengan load balancing
  - Rate limiting untuk security
  - Health monitoring

- **❤️ Health Check**: http://localhost/health
  - Status semua services
  - Response time monitoring
  - Load balancer status

### Tools Management & Monitoring:
- **🗄️ Database Admin (pgAdmin)**: http://localhost:5050
  - Email: `admin@example.com`
  - Password: `admin123`
  - Manage PostgreSQL database

- **📊 Monitoring Dashboard**: http://localhost:3001 (jika Grafana enabled)
  - Username: `admin`
  - Password: `admin123`
  - Real-time metrics & charts

- **🔍 Metrics (Prometheus)**: http://localhost:9090 (jika enabled)
  - Raw metrics data
  - Query interface
  - Alerting rules

### API Testing Examples:
```bash
# Health check
curl http://localhost/health

# Get all todos
curl http://localhost/todos

# Create new todo
curl -X POST http://localhost/todos \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Learn Docker Compose",
    "completed": false,
    "description": "Master container orchestration"
  }'

# Update todo
curl -X PATCH http://localhost/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'

# Get statistics
curl http://localhost/stats
```

## 🧪 Menjalankan Load Testing (Updated)

### Persiapan Load Testing:

1. **Install Python dependencies (Modern way)**
   ```bash
   # Menggunakan pip
   pip install -r tests/requirements.txt
   
   # Atau menggunakan pipenv (recommended)
   pipenv install -r tests/requirements.txt
   pipenv shell
   
   # Atau menggunakan conda
   conda create -n todo-test python=3.11
   conda activate todo-test
   pip install -r tests/requirements.txt
   ```

2. **Verifikasi aplikasi ready**
   ```bash
   # Health check
   curl -f http://localhost/health || echo "App not ready"
   
   # Quick connectivity test
   python -c "import requests; print('✅ OK' if requests.get('http://localhost/health').status_code == 200 else '❌ FAIL')"
   ```

### Menjalankan Test Suite:

#### 🎯 Opsi A: Interactive Menu (Recommended)
```bash
# Windows
cd tests
run_tests.bat

# macOS/Linux
cd tests
chmod +x run_tests.sh
./run_tests.sh
```

#### 🎯 Opsi B: Individual Tests
```bash
# 1. Simple Load Test (Beginner friendly)
python tests/simple_load_test.py

# 2. Comprehensive Load Test
python tests/load_test.py --users 15 --duration 120 --save

# 3. Stress Test (Find breaking point)
python tests/stress_test.py --max-users 200 --ramp-up 300

# 4. Docker Container Monitoring
python tests/docker_load_test.py --users 10 --duration 60

# 5. Custom scenarios
python tests/load_test.py \
  --users 25 \
  --duration 180 \
  --url http://localhost \
  --save \
  --output-file results_$(date +%Y%m%d_%H%M%S).json
```

#### 🎯 Opsi C: Automated CI/CD Testing
```bash
# Run all tests in sequence
python tests/run_all_tests.py

# Generate comprehensive report
python tests/generate_report.py --input results/ --output report.html
```

### Advanced Load Testing:

#### Multi-scenario Testing:
```bash
# Test different user behaviors
python tests/scenario_test.py \
  --scenario heavy_read \
  --users 50 \
  --duration 300

python tests/scenario_test.py \
  --scenario heavy_write \
  --users 20 \
  --duration 180
```

#### Performance Benchmarking:
```bash
# Baseline performance test
python tests/benchmark.py --baseline

# Compare with previous results
python tests/benchmark.py --compare baseline_results.json
```

## 🔍 Troubleshooting (Updated 2026)

### Masalah Umum dan Solusi Modern:

#### 1. Docker Desktop Issues
**Error**: `Cannot connect to the Docker daemon` atau `Docker Desktop starting...`

**Solusi**:
```bash
# Windows - Reset Docker Desktop
"C:\Program Files\Docker\Docker\Docker Desktop.exe" --reset-to-factory

# macOS - Reset Docker Desktop
~/Applications/Docker.app/Contents/MacOS/Docker --reset-to-factory

# Linux - Restart Docker service
sudo systemctl restart docker
sudo usermod -aG docker $USER
newgrp docker
```

#### 2. Port Conflicts (Modern approach)
**Error**: `Port 80/8080 is already in use`

**Solusi**:
```bash
# Check what's using the port
netstat -tulpn | grep :80
# atau
lsof -i :80

# Kill process using port
sudo kill -9 $(lsof -t -i:80)

# Or use different ports
export FRONTEND_PORT=3000
export API_PORT=8000
docker compose up -d
```

#### 3. Memory/Performance Issues
**Error**: Slow performance, high CPU/Memory usage

**Solusi**:
```bash
# Check Docker resource usage
docker stats --no-stream

# Optimize Docker Desktop settings
# Settings → Resources → Advanced:
# - Memory: 8GB+ (for load testing)
# - CPUs: 6+ cores
# - Enable VirtioFS (macOS)
# - Enable WSL 2 (Windows)

# Clean up Docker system
docker system prune -af --volumes
docker builder prune -af
```

#### 4. Database Connection Issues
**Error**: `relation "todos" does not exist` atau connection timeouts

**Solusi**:
```bash
# Method 1: Reset database with proper initialization
docker compose down -v
docker compose up -d postgres
sleep 30  # Wait for postgres to be ready
docker compose up -d

# Method 2: Manual database setup
docker exec -it $(docker compose ps -q postgres) psql -U todouser -d tododb -c "
CREATE TABLE IF NOT EXISTS todos (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO todos (title, completed, description) VALUES 
('Learn Docker', false, 'Master containerization'),
('Build API', true, 'Create REST API'),
('Setup Load Balancer', false, 'Configure Nginx')
ON CONFLICT DO NOTHING;"

# Method 3: Check database logs
docker compose logs postgres -f
```

#### 5. Network Issues
**Error**: Services can't communicate, DNS resolution fails

**Solusi**:
```bash
# Recreate network
docker compose down
docker network prune -f
docker compose up -d

# Check network connectivity
docker compose exec api1 ping postgres
docker compose exec api1 nslookup redis

# Debug network issues
docker network ls
docker network inspect $(docker compose ps --format json | jq -r '.[0].Networks' | head -1)
```

#### 6. Build Issues
**Error**: Build failures, dependency issues

**Solusi**:
```bash
# Clean build (no cache)
docker compose build --no-cache --pull

# Build specific service
docker compose build api1

# Check build logs
docker compose build api1 --progress=plain

# Update base images
docker compose pull
docker compose up -d --build
```

#### 7. Load Testing Issues
**Error**: High error rates, timeouts during testing

**Solusi**:
```bash
# Scale up services before testing
docker compose up -d --scale api1=3 --scale api2=3 --scale api3=3

# Increase resource limits
# Edit docker-compose.yml:
# deploy:
#   resources:
#     limits:
#       memory: 1G
#       cpus: '1.0'

# Monitor during testing
watch -n 1 'docker stats --no-stream'

# Check rate limiting
curl -v http://localhost/todos  # Look for 429 status codes
```

### Advanced Debugging:

#### Container Health Debugging:
```bash
# Check health status
docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Health}}"

# Inspect health check logs
docker inspect $(docker compose ps -q api1) | jq '.[0].State.Health'

# Manual health check
docker compose exec api1 curl -f http://localhost:3000/health
```

#### Performance Profiling:
```bash
# CPU profiling
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

# Memory analysis
docker compose exec api1 node --inspect=0.0.0.0:9229 server.js
# Then connect Chrome DevTools to localhost:9229

# Database performance
docker compose exec postgres psql -U todouser -d tododb -c "
SELECT query, calls, total_time, mean_time 
FROM pg_stat_statements 
ORDER BY total_time DESC LIMIT 10;"
```

## 📊 Monitoring Aplikasi (Enhanced)

### Real-time Monitoring:

#### Container Status & Health:
```bash
# Comprehensive status check
docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}\t{{.Health}}"

# Watch mode (auto-refresh)
watch -n 2 'docker compose ps'

# Health check all services
docker compose exec api1 curl -s http://localhost:3000/health | jq
docker compose exec nginx curl -s http://localhost/nginx-health
```

#### Resource Monitoring:
```bash
# Real-time resource usage
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"

# Memory usage breakdown
docker compose exec api1 cat /proc/meminfo | head -5

# Disk usage
docker system df -v
```

#### Application Logs (Structured):
```bash
# All services with timestamps
docker compose logs -f --timestamps

# Specific service with filtering
docker compose logs api1 -f --tail=100 | grep ERROR

# JSON formatted logs
docker compose logs --json api1 | jq '.log'

# Export logs for analysis
docker compose logs --no-color > app_logs_$(date +%Y%m%d_%H%M%S).log
```

### Performance Metrics:

#### Database Performance:
```bash
# Connection stats
docker compose exec postgres psql -U todouser -d tododb -c "
SELECT datname, numbackends, xact_commit, xact_rollback, blks_read, blks_hit 
FROM pg_stat_database WHERE datname = 'tododb';"

# Query performance
docker compose exec postgres psql -U todouser -d tododb -c "
SELECT query, calls, total_time, mean_time, rows 
FROM pg_stat_statements 
ORDER BY total_time DESC LIMIT 5;"

# Table statistics
docker compose exec postgres psql -U todouser -d tododb -c "
SELECT schemaname, tablename, n_tup_ins, n_tup_upd, n_tup_del 
FROM pg_stat_user_tables;"
```

#### Redis Performance:
```bash
# Redis info
docker compose exec redis redis-cli info stats | grep -E "(keyspace|memory|cpu)"

# Monitor commands
docker compose exec redis redis-cli monitor

# Memory usage
docker compose exec redis redis-cli info memory | grep used_memory_human
```

#### API Performance:
```bash
# Response time testing
curl -w "@curl-format.txt" -o /dev/null -s http://localhost/todos

# Create curl-format.txt:
echo "     time_namelookup:  %{time_namelookup}s
        time_connect:  %{time_connect}s
     time_appconnect:  %{time_appconnect}s
    time_pretransfer:  %{time_pretransfer}s
       time_redirect:  %{time_redirect}s
  time_starttransfer:  %{time_starttransfer}s
                     ----------
          time_total:  %{time_total}s" > curl-format.txt
```

### Advanced Monitoring Setup:

#### Prometheus + Grafana (Optional):
```bash
# Enable monitoring stack
docker compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d

# Access Grafana: http://localhost:3001
# Access Prometheus: http://localhost:9090
```

#### Custom Metrics Collection:
```bash
# Create monitoring script
cat > monitor.sh << 'EOF'
#!/bin/bash
while true; do
    echo "$(date): $(curl -s http://localhost/health)" >> health.log
    echo "$(date): $(docker stats --no-stream --format 'table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}')" >> resources.log
    sleep 30
done
EOF

chmod +x monitor.sh
./monitor.sh &
```

## 🛑 Menghentikan Aplikasi (Safe Shutdown)

### Graceful Shutdown (Recommended):
```bash
# Stop semua services dengan graceful shutdown
docker compose stop

# Tunggu semua container berhenti dengan aman
docker compose ps  # Verify all stopped
```

### Complete Shutdown:
```bash
# Stop dan remove containers (data tetap ada)
docker compose down

# Stop dan remove dengan networks
docker compose down --remove-orphans
```

### Full Reset (Development):
```bash
# HATI-HATI: Ini akan menghapus SEMUA data!
docker compose down -v --remove-orphans

# Clean up everything
docker system prune -af --volumes
```

### Selective Service Management:
```bash
# Stop specific service
docker compose stop api1

# Restart specific service
docker compose restart nginx

# Remove and recreate specific service
docker compose rm -f api1
docker compose up -d api1
```

## 🔄 Update & Maintenance (Modern Workflow)

### Development Updates:
```bash
# Hot reload untuk development
docker compose watch  # Requires Docker Compose 2.22+

# Manual rebuild setelah code changes
docker compose build api1 api2 api3
docker compose up -d --no-deps api1 api2 api3
```

### Production Updates (Zero Downtime):
```bash
# Rolling update strategy
docker compose up -d --scale api1=6  # Scale up
sleep 30  # Wait for new instances
docker compose up -d --scale api1=3  # Scale back down

# Blue-green deployment
docker compose -f docker-compose.blue.yml up -d
# Test blue environment
# Switch traffic
docker compose -f docker-compose.green.yml down
```

### Database Migrations:
```bash
# Backup before migration
docker compose exec postgres pg_dump -U todouser tododb > backup_$(date +%Y%m%d).sql

# Run migrations
docker compose exec postgres psql -U todouser -d tododb -f /migrations/001_add_new_column.sql

# Verify migration
docker compose exec postgres psql -U todouser -d tododb -c "\d todos"
```

### Security Updates:
```bash
# Update base images
docker compose pull
docker compose up -d --build

# Scan for vulnerabilities
docker scout cves $(docker compose images -q)

# Update dependencies
docker compose build --no-cache --pull
```

## 📱 Menggunakan Aplikasi

### Melalui Web Interface (http://localhost:8080):
1. Buka browser ke http://localhost:8080
2. Tambah todo baru dengan mengisi form
3. Klik checkbox untuk mark as completed
4. Lihat statistik di bagian bawah

### Melalui API (untuk developer):
```bash
# GET - Lihat semua todos
curl http://localhost/todos

# POST - Tambah todo baru
curl -X POST http://localhost/todos \
  -H "Content-Type: application/json" \
  -d '{"title":"Belajar Docker","completed":false,"description":"Tutorial Docker"}'

# PATCH - Update todo
curl -X PATCH http://localhost/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"completed":true}'

# DELETE - Hapus todo
curl -X DELETE http://localhost/todos/1
```

## 🎯 Tips Penggunaan (Best Practices 2026)

### Development Workflow:
```bash
# 1. Start development environment
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# 2. Enable file watching (auto-reload)
docker compose watch

# 3. View logs in real-time
docker compose logs -f api1

# 4. Debug specific service
docker compose exec api1 /bin/sh
```

### Performance Optimization:
```bash
# 1. Enable BuildKit for faster builds
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# 2. Use multi-stage builds
# Already implemented in Dockerfile

# 3. Optimize Docker Desktop
# Settings → Resources → File Sharing: Only add necessary paths
# Settings → Docker Engine: Enable experimental features

# 4. Use .dockerignore
echo "node_modules
.git
*.log
.env.local" > .dockerignore
```

### Production Readiness:
```bash
# 1. Environment-specific configs
cp .env.example .env.production
# Edit .env.production with production values

# 2. Health checks
curl -f http://localhost/health || exit 1

# 3. Resource monitoring
docker stats --no-stream | awk 'NR>1 {if($3+0>80) print $1" high CPU: "$3}'

# 4. Backup automation
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker compose exec postgres pg_dump -U todouser tododb | gzip > backups/backup_$DATE.sql.gz
find backups/ -name "*.sql.gz" -mtime +7 -delete
EOF
```

### Security Best Practices:
```bash
# 1. Use secrets for sensitive data
echo "my_secret_password" | docker secret create db_password -

# 2. Run containers as non-root
# Already implemented in Dockerfile

# 3. Network security
docker network create --driver overlay --encrypted secure-network

# 4. Regular security scans
docker scout quickview
docker scout cves --only-severity critical,high
```

### Scaling Strategies:
```bash
# Horizontal scaling
docker compose up -d --scale api1=5 --scale api2=5 --scale api3=5

# Load testing before scaling
python tests/stress_test.py --max-users 100

# Monitor during scaling
watch -n 1 'docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"'
```

## 📞 Bantuan Lebih Lanjut

Jika masih ada masalah:

1. **Cek logs aplikasi**:
   ```cmd
   docker-compose logs api1
   ```

2. **Restart Docker Desktop**

3. **Reset semua containers**:
   ```cmd
   docker-compose down -v
   docker system prune -f
   docker-compose up -d
   ```

4. **Cek dokumentasi Docker**: https://docs.docker.com/

---

**Selamat menggunakan Todo App! 🎉**

Aplikasi sudah siap digunakan dengan fitur:
- ✅ Multi-instance API dengan load balancing
- ✅ Database PostgreSQL dengan persistence
- ✅ Redis caching untuk performance
- ✅ Web interface yang user-friendly
- ✅ Load testing tools
- ✅ Monitoring dan health checks