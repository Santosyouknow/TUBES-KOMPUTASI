# Docker Swarm Deployment Script (PowerShell)
# Usage: .\scripts\deploy.ps1 [dev|prod]

param(
    [Parameter(Position=0)]
    [ValidateSet("dev", "prod")]
    [string]$Environment = "prod"
)

$ErrorActionPreference = "Stop"
$StackName = "todo-app"

Write-Host "🚀 Deploying Todo App to Docker Swarm..." -ForegroundColor Green
Write-Host "Environment: $Environment" -ForegroundColor Yellow
Write-Host "Stack Name: $StackName" -ForegroundColor Yellow

# Check if Docker Swarm is initialized
$dockerInfo = docker info 2>$null
if ($dockerInfo -notmatch "Swarm: active") {
    Write-Host "❌ Docker Swarm is not initialized. Please run 'docker swarm init' first." -ForegroundColor Red
    exit 1
}

# Check if we're on a manager node
$nodeInfo = docker node ls 2>$null
if ($nodeInfo -notmatch "Leader") {
    Write-Host "❌ This node is not a Swarm manager. Please run this script on a manager node." -ForegroundColor Red
    exit 1
}

# Create necessary directories for persistent data
Write-Host "📁 Creating data directories..." -ForegroundColor Blue
New-Item -ItemType Directory -Force -Path "/data/postgres" | Out-Null
New-Item -ItemType Directory -Force -Path "/data/pgadmin" | Out-Null
New-Item -ItemType Directory -Force -Path "/data/postgres-dev" | Out-Null

# Load environment variables
$envFile = ".env.$Environment"
if (Test-Path $envFile) {
    Write-Host "📝 Loading environment variables from $envFile" -ForegroundColor Blue
    Get-Content $envFile | Where-Object { $_ -notmatch '^#' -and $_ -match '=' } | ForEach-Object {
        $key, $value = $_.split('=', 2)
        [System.Environment]::SetEnvironmentVariable($key, $value)
    }
}
elseif (Test-Path ".env") {
    Write-Host "📝 Loading environment variables from .env" -ForegroundColor Blue
    Get-Content ".env" | Where-Object { $_ -notmatch '^#' -and $_ -match '=' } | ForEach-Object {
        $key, $value = $_.split('=', 2)
        [System.Environment]::SetEnvironmentVariable($key, $value)
    }
}
else {
    Write-Host "⚠️  No environment file found, using defaults" -ForegroundColor Yellow
}

# Choose the right compose file
if ($Environment -eq "dev") {
    $ComposeFile = "docker-stack-dev.yml"
}
else {
    $ComposeFile = "docker-stack.yml"
}

Write-Host "📋 Using compose file: $ComposeFile" -ForegroundColor Blue

# Pull latest images
Write-Host "📦 Pulling latest images..." -ForegroundColor Blue
docker-compose -f $ComposeFile pull

# Deploy the stack
Write-Host "🔥 Deploying stack..." -ForegroundColor Blue
docker stack deploy -c $ComposeFile $StackName --with-registry-auth

# Wait for services to be ready
Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Blue
Start-Sleep -Seconds 30

# Show service status
Write-Host "📊 Service Status:" -ForegroundColor Green
docker stack services $StackName

# Show stack tasks
Write-Host "📋 Stack Tasks:" -ForegroundColor Green
docker stack ps $StackName

Write-Host ""
Write-Host "✅ Deployment completed!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Access URLs:" -ForegroundColor Cyan
Write-Host "  - Main App: http://localhost"
Write-Host "  - Frontend: http://localhost:8080"
Write-Host "  - pgAdmin: http://localhost:5050"
Write-Host ""
Write-Host "🔍 Useful commands:" -ForegroundColor Cyan
Write-Host "  - View logs: docker service logs ${StackName}_api"
Write-Host "  - Scale API: docker service scale ${StackName}_api=5"
Write-Host "  - Update stack: docker stack deploy -c $ComposeFile $StackName"
Write-Host "  - Remove stack: docker stack rm $StackName"
Write-Host ""
Write-Host "💡 Health checks:" -ForegroundColor Cyan
Write-Host "  - API Health: curl http://localhost/health"
Write-Host "  - Nginx Status: curl http://localhost/nginx-status"
