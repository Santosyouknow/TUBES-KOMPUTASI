# Load Testing untuk Todo App

Kumpulan script Python untuk melakukan load testing pada aplikasi Todo.

## 📋 Daftar Test

### 1. Simple Load Test (`simple_load_test.py`)
- **Tujuan**: Testing dasar dengan beban ringan
- **Default**: 5 users, 30 detik
- **Cocok untuk**: Development testing, quick check

### 2. Load Test (`load_test.py`)
- **Tujuan**: Comprehensive load testing dengan metrics detail
- **Default**: 10 users, 60 detik
- **Features**: 
  - Response time statistics
  - Success rate analysis
  - Endpoint performance breakdown
  - JSON report export

### 3. Stress Test (`stress_test.py`)
- **Tujuan**: Mencari breaking point sistem
- **Default**: Ramp up hingga 100 users dalam 5 menit
- **Features**:
  - Gradual user increase
  - Real-time monitoring
  - Breaking point detection
  - Performance degradation analysis

## 🚀 Cara Menggunakan

### Persiapan

1. **Install Python** (3.7+)
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Pastikan aplikasi Todo berjalan**:
   ```bash
   docker-compose up -d
   ```

### Menjalankan Test

#### Opsi 1: Menggunakan Script Batch (Windows)
```cmd
run_tests.bat
```

#### Opsi 2: Manual

**Simple Load Test:**
```bash
python simple_load_test.py
```

**Load Test dengan parameter custom:**
```bash
python load_test.py --users 20 --duration 120 --url http://localhost --save
```

**Stress Test:**
```bash
python stress_test.py --max-users 50 --ramp-up 180
```

## 📊 Parameter yang Bisa Disesuaikan

### Load Test
- `--users`: Jumlah concurrent users (default: 10)
- `--duration`: Durasi test dalam detik (default: 60)
- `--url`: Base URL aplikasi (default: http://localhost)
- `--save`: Simpan hasil detail ke file JSON

### Stress Test
- `--max-users`: Maksimum users untuk testing (default: 100)
- `--ramp-up`: Waktu untuk mencapai max users dalam detik (default: 300)
- `--url`: Base URL aplikasi (default: http://localhost)

## 📈 Interpretasi Hasil

### Metrics yang Diukur

1. **Response Time**
   - Average: Rata-rata waktu response
   - 95th Percentile: 95% request selesai dalam waktu ini
   - Maximum: Response time terlama

2. **Success Rate**
   - Persentase request yang berhasil (status code < 400)
   - Target: > 99%

3. **Requests per Second (RPS)**
   - Throughput sistem
   - Semakin tinggi semakin baik

4. **Error Rate**
   - Persentase request yang gagal
   - Target: < 1%

### Benchmark Performance

| Load Level | Users | Expected RPS | Max Response Time |
|------------|-------|--------------|-------------------|
| Light      | 1-10  | 50-100       | < 200ms          |
| Medium     | 10-50 | 100-300      | < 500ms          |
| Heavy      | 50-100| 200-500      | < 1000ms         |

## 🔧 Troubleshooting

### Error: Connection Refused
```
Solusi: Pastikan aplikasi berjalan di http://localhost
docker-compose ps
```

### Error: Timeout
```
Solusi: 
1. Cek resource sistem (CPU, Memory)
2. Kurangi jumlah concurrent users
3. Increase timeout di script
```

### High Error Rate
```
Kemungkinan penyebab:
1. Database connection limit tercapai
2. Memory habis
3. CPU overload
4. Network bottleneck
```

## 📝 Contoh Output

### Load Test Results
```
LOAD TEST RESULTS
==========================================
Test Duration: 60.00 seconds
Number of Users: 10
Total Requests: 1250
Successful Requests: 1245
Failed Requests: 5
Success Rate: 99.60%
Requests per Second: 20.83

RESPONSE TIME STATISTICS:
  Average: 145.30 ms
  Minimum: 23.10 ms
  Maximum: 890.20 ms
  95th Percentile: 320.50 ms

ENDPOINT PERFORMANCE:
  GET /todos: 142.30 ms avg (625 requests)
  POST /todos: 148.90 ms avg (312 requests)
  GET /health: 89.20 ms avg (313 requests)
```

### Stress Test Breaking Point
```
PERFORMANCE BY USER COUNT:
----------------------------------------------------------
  0- 9 users: Avg RT:  145.3ms | Error Rate:  0.0% | ✅ Good
 10-19 users: Avg RT:  234.7ms | Error Rate:  0.2% | ✅ Good
 20-29 users: Avg RT:  456.8ms | Error Rate:  1.1% | ✅ Good
 30-39 users: Avg RT:  789.2ms | Error Rate:  3.4% | ✅ Good
 40-49 users: Avg RT: 1234.5ms | Error Rate:  8.7% | ❌ Degraded

🔥 BREAKING POINT DETECTED: ~40 concurrent users
```

## 🎯 Tips Optimasi

Berdasarkan hasil testing, berikut rekomendasi optimasi:

1. **Response Time > 500ms**:
   - Optimize database queries
   - Add database indexing
   - Implement connection pooling

2. **Error Rate > 5%**:
   - Increase database connection limit
   - Add retry mechanism
   - Implement circuit breaker

3. **Low RPS**:
   - Scale horizontally (add more API instances)
   - Implement caching (Redis)
   - Optimize application code

4. **Memory Issues**:
   - Increase container memory limits
   - Fix memory leaks
   - Implement garbage collection tuning