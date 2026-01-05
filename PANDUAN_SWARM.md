# PANDUAN DEPLOYMENT DOCKER SWARM

## Daftar Isi
1. [Prasyarat](#prasyarat)
2. [Inisialisasi Docker Swarm](#inisialisasi-docker-swarm)
3. [Konfigurasi Environment](#konfigurasi-environment)
4. [Deployment](#deployment)
5. [Scaling dan Management](#scaling-dan-management)
6. [Monitoring](#monitoring)
7. [Troubleshooting](#troubleshooting)

## Prasyarat

### Software yang Diperlukan
- Docker Engine (versi 20.10+)
- Docker Swarm (sudah termasuk dalam Docker)
- PowerShell (Windows) atau Bash (Linux/Mac)

### Hardware Requirements
- **Minimum**: 2 CPU cores, 4GB RAM, 20GB storage
- **Recommended**: 4 CPU cores, 8GB RAM, 50GB storage
- **Production**: 8+ CPU cores, 16GB+ RAM, 100GB+ storage

### Network Requirements
- Port 80 (HTTP)
- Port 8080 (Frontend)
- Port 5050 (pgAdmin)
- Port 2377 (Swarm management)
- Ports 7946 (Swarm communication)

## Inisialisasi Docker Swarm

### Single Node Cluster (Development)
```bash
# Inisialisasi Swarm sebagai manager
docker swarm init

# Untuk multi-node, gunakan:
docker swarm init --advertise-addr <IP_ADDRESS>
```

### Multi-Node Cluster (Production)
```bash
# Pada manager node:
docker swarm init --advertise-addr <MANAGER_IP>

# Pada worker nodes, join dengan token dari manager:
docker swarm join --token <TOKEN> <MANAGER_IP>:2377
```

### Verifikasi Swarm Status
```bash
# Cek status Swarm
docker info | grep Swarm

# Lihat node yang terdaftar
docker node ls
```

## Konfigurasi Environment

### 1. Salin File Environment
```bash
# Untuk production
cp .env.example .env

# Untuk development
cp .env.example .env.dev
```

### 2. Edit File Environment
Edit file `.env` sesuai kebutuhan:

```bash
# Database Configuration
DB_USER=todouser
DB_PASSWORD=your_secure_password
DB_NAME=tododb

# pgAdmin Configuration
PGADMIN_EMAIL=your-email@example.com
PGADMIN_PASSWORD=your_admin_password

# Scaling Configuration
API_REPLICAS=3
FRONTEND_REPLICAS=2
```

### 3. Buat Data Directories
```bash
# Linux/Mac
sudo mkdir -p /data/{postgres,pgadmin,postgres-dev}
sudo chown -R 999:999 /data/postgres
sudo chown -R 5050:5050 /data/pgadmin

# Windows (PowerShell as Administrator)
New-Item -ItemType Directory -Force -Path "/data/postgres"
New-Item -ItemType Directory -Force -Path "/data/pgadmin"
New-Item -ItemType Directory -Force -Path "/data/postgres-dev"
```

## Deployment

### Deployment Production
```bash
# Menggunakan PowerShell (Windows)
.\scripts\deploy.ps1 prod

# Menggunakan Bash (Linux/Mac)
./scripts/deploy.sh prod
```

### Deployment Development
```bash
# PowerShell
.\scripts\deploy.ps1 dev

# Bash
./scripts/deploy.sh dev
```

### Manual Deployment
```bash
# Production
docker stack deploy -c docker-stack.yml todo-app

# Development
docker stack deploy -c docker-stack-dev.yml todo-app
```

## Scaling dan Management

### Melihat Status Services
```bash
# Lihat semua services
docker stack services todo-app

# Lihat detail tasks
docker stack ps todo-app

# Lihat logs service tertentu
docker service logs todo-app_api
```

### Scaling Services
```bash
# Scale API ke 5 replicas
docker service scale todo-app_api=5

# Scale Frontend ke 3 replicas
docker service scale todo-app_frontend=3

# Scale multiple services sekaligus
docker service scale todo-app_api=5 todo-app_frontend=3
```

### Update Services
```bash
# Update seluruh stack
docker stack deploy -c docker-stack.yml todo-app --resolve-image changed

# Update service tertentu
docker service update --image new-image todo-app_api
```

### Remove Stack
```bash
# Hapus seluruh stack
docker stack rm todo-app

# Hapus dengan force cleanup
docker stack rm todo-app && docker system prune -f
```

## Monitoring

### Health Checks
```bash
# Cek health API
curl http://localhost/health

# Cek health backend
curl http://localhost/backend-health

# Cek status nginx
curl http://localhost/nginx-status
```

### Monitoring Commands
```bash
# Real-time logs
docker service logs -f todo-app_api

# Monitor resource usage
docker stats

# Lihat node status
docker node ls

# Inspect service
docker service inspect todo-app_api
```

### Service Discovery
```bash
# Test DNS resolution
docker run --rm --network todo-app_app-network alpine nslookup api

# Test connectivity
docker run --rm --network todo-app_app-network alpine ping api
```

## Troubleshooting

### Common Issues

#### 1. Service tidak starting
```bash
# Cek service status
docker service ps todo-app_api

# Lihat error logs
docker service logs todo-app_api

# Restart service
docker service update --force todo-app_api
```

#### 2. Database connection issues
```bash
# Cek database health
docker exec -it $(docker ps -q -f name=postgres) pg_isready -U todouser

# Lihat database logs
docker service logs todo-app_postgres
```

#### 3. Load balancing issues
```bash
# Test nginx configuration
docker exec -it $(docker ps -q -f name=nginx) nginx -t

# Reload nginx
docker exec -it $(docker ps -q -f name=nginx) nginx -s reload
```

#### 4. Resource constraints
```bash
# Cek resource usage
docker service inspect todo-app_api --format '{{.Spec.TaskTemplate.Resources}}'

# Update resource limits
docker service update --limit-cpu 1.0 --limit-memory 1G todo-app_api
```

### Recovery Procedures

#### Service Recovery
```bash
# Restart service yang failed
docker service update --force todo-app_api

# Rollback ke versi sebelumnya
docker service rollback todo-app_api
```

#### Node Recovery
```bash
# Drain node untuk maintenance
docker node update --availability drain <NODE_ID>

# Reactivate node
docker node update --availability active <NODE_ID>

# Remove node dari swarm
docker swarm leave --force
```

### Performance Tuning

#### Optimization Tips
1. **Resource Limits**: Sesuaikan CPU dan memory limits di `docker-stack.yml`
2. **Replica Count**: Sesuaikan jumlah replicas berdasarkan load
3. **Health Checks**: Optimalkan interval dan timeout health checks
4. **Network**: Gunakan overlay network yang encrypted
5. **Storage**: Gunakan SSD untuk database storage

#### Monitoring Metrics
- Response time API
- Error rate
- CPU dan memory usage
- Database connection pool
- Redis hit rate

## Advanced Configuration

### Secrets Management
```bash
# Buat secrets untuk production
echo "your_db_password" | docker secret create db_password -

# Update stack untuk menggunakan secrets
docker secret ls
```

### Config Management
```bash
# Buat config untuk nginx
docker config create nginx_config ./nginx-swarm.conf

# Gunakan config di stack
```

### Multi-Region Deployment
```bash
# Label nodes untuk placement
docker node update --label-add region=asia <NODE_ID>
docker node update --label-add region=europe <NODE_ID>

# Gunakan placement constraints di docker-stack.yml
```

## Security Best Practices

1. **Network Security**: Gunakan encrypted overlay networks
2. **Image Security**: Gunakan image yang signed dan scanned
3. **Secrets**: Jangan simpan passwords di environment variables
4. **Access Control**: Implement RBAC untuk Docker Swarm
5. **Regular Updates**: Update images dan dependencies secara berkala

## Backup and Recovery

### Database Backup
```bash
# Backup database
docker exec todo-app_postgres.1.<id> pg_dump -U todouser tododb > backup.sql

# Restore database
docker exec -i todo-app_postgres.1.<id> psql -U todouser tododb < backup.sql
```

### Volume Backup
```bash
# Backup volumes
docker run --rm -v /data/postgres:/data -v $(pwd):/backup alpine tar czf /backup/postgres-backup.tar.gz /data
```

---

## Quick Reference

### Essential Commands
```bash
# Deploy
docker stack deploy -c docker-stack.yml todo-app

# Scale
docker service scale todo-app_api=5

# Logs
docker service logs -f todo-app_api

# Status
docker stack services todo-app

# Remove
docker stack rm todo-app
```

### Access URLs
- **Main App**: http://localhost
- **Frontend**: http://localhost:8080  
- **pgAdmin**: http://localhost:5050
- **Health Check**: http://localhost/health

Untuk bantuan lebih lanjut, hubungi tim DevOps.
