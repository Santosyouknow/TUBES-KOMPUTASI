# ⚡ Quick Start - Todo App (Updated 2026)

## 🚀 Cara Tercepat Menjalankan Program

### 1. Persiapan (Sekali saja)
1. **Install Docker Desktop 4.0+**: [Download di sini](https://www.docker.com/products/docker-desktop/)
2. **Konfigurasi Docker Desktop**:
   - Memory: 6GB+ (Settings → Resources)
   - CPUs: 4+ cores
   - Enable WSL 2 (Windows) / VirtioFS (macOS)
3. **Buka Docker Desktop** dan tunggu sampai siap (ikon whale hijau)

### 2. Jalankan Program (Super Mudah!)

**Opsi A: Script Otomatis (Recommended)**
```cmd
# Windows - Double-click atau run di Command Prompt:
START_APP.bat

# macOS/Linux:
chmod +x start_app.sh
./start_app.sh
```

**Opsi B: Modern Docker Compose**
```bash
# 1. Navigate ke folder project
cd /path/to/todo-app

# 2. Jalankan dengan Docker Compose V2
docker compose up -d --build

# 3. Tunggu 2-3 menit, lalu buka browser ke:
# http://localhost:8080
```

**Opsi C: One-liner (Advanced)**
```bash
git clone <repo-url> && cd todo-app && docker compose up -d --build && sleep 120 && open http://localhost:8080
```

### 3. Akses Aplikasi
- **🌐 Web App**: http://localhost:8080 ← **Buka ini untuk menggunakan aplikasi**
- **🔌 API**: http://localhost/todos
- **🗄️ Database Admin**: http://localhost:5050 (admin@example.com / admin123)
- **❤️ Health Check**: http://localhost/health

### 4. Stop Program
```bash
# Graceful shutdown
docker compose stop

# Complete cleanup
docker compose down -v
```

---

## 🎯 Itu saja! Super simple kan?

### Jika ada masalah:
1. **Pastikan Docker Desktop berjalan** dan allocated 6GB+ RAM
2. **Fresh install**: Jalankan `START_APP.bat` → pilih opsi 2
3. **Manual reset**:
   ```bash
   docker compose down -v
   docker system prune -af
   docker compose up -d --build
   ```
4. **Tunggu 3-5 menit** untuk full startup
5. **Buka http://localhost:8080**

### Load Testing (Opsional):
```bash
# Install dependencies
pip install -r tests/requirements.txt

# Quick test
cd tests
python simple_load_test.py

# Comprehensive test
python load_test.py --users 10 --duration 60

# Stress test
python stress_test.py --max-users 50
```

### Modern Features:
- ✅ **Auto-scaling**: 3 API instances dengan load balancing
- ✅ **Health monitoring**: Real-time status checks
- ✅ **Rate limiting**: Built-in security protection
- ✅ **Caching**: Redis untuk performance optimization
- ✅ **Database**: PostgreSQL dengan persistence
- ✅ **Monitoring**: Container resource tracking
- ✅ **Load testing**: Comprehensive testing suite

**Selamat menggunakan Todo App! 🎉**

### Quick Commands:
```bash
# Status check
docker compose ps

# View logs
docker compose logs -f

# Resource usage
docker stats --no-stream

# Scale services
docker compose up -d --scale api1=5

# Health check
curl http://localhost/health
```