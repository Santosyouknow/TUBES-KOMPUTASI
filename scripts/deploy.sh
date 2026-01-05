#!/bin/bash

# Docker Swarm Deployment Script
# Usage: ./scripts/deploy.sh [dev|prod]

set -e

ENVIRONMENT=${1:-prod}
STACK_NAME="todo-app"

echo "🚀 Deploying Todo App to Docker Swarm..."
echo "Environment: $ENVIRONMENT"
echo "Stack Name: $STACK_NAME"

# Check if Docker Swarm is initialized
if ! docker info | grep -q "Swarm: active"; then
    echo "❌ Docker Swarm is not initialized. Please run 'docker swarm init' first."
    exit 1
fi

# Check if we're on a manager node
if ! docker node ls | grep -q "Leader"; then
    echo "❌ This node is not a Swarm manager. Please run this script on a manager node."
    exit 1
fi

# Create necessary directories for persistent data
echo "📁 Creating data directories..."
sudo mkdir -p /data/postgres
sudo mkdir -p /data/pgadmin
sudo mkdir -p /data/postgres-dev
sudo chown -R 999:999 /data/postgres
sudo chown -R 5050:5050 /data/pgadmin

# Load environment variables
if [ -f ".env.$ENVIRONMENT" ]; then
    echo "📝 Loading environment variables from .env.$ENVIRONMENT"
    export $(cat .env.$ENVIRONMENT | grep -v '^#' | xargs)
elif [ -f ".env" ]; then
    echo "📝 Loading environment variables from .env"
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "⚠️  No environment file found, using defaults"
fi

# Choose the right compose file
if [ "$ENVIRONMENT" = "dev" ]; then
    COMPOSE_FILE="docker-stack-dev.yml"
else
    COMPOSE_FILE="docker-stack.yml"
fi

echo "📋 Using compose file: $COMPOSE_FILE"

# Pull latest images
echo "📦 Pulling latest images..."
docker-compose -f $COMPOSE_FILE pull

# Deploy the stack
echo "🔥 Deploying stack..."
docker stack deploy -c $COMPOSE_FILE $STACK_NAME --with-registry-auth

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Show service status
echo "📊 Service Status:"
docker stack services $STACK_NAME

# Show stack tasks
echo "📋 Stack Tasks:"
docker stack ps $STACK_NAME

echo ""
echo "✅ Deployment completed!"
echo ""
echo "🌐 Access URLs:"
echo "  - Main App: http://localhost"
echo "  - Frontend: http://localhost:8080"
echo "  - pgAdmin: http://localhost:5050"
echo ""
echo "🔍 Useful commands:"
echo "  - View logs: docker service logs $STACK_NAME_api"
echo "  - Scale API: docker service scale $STACK_NAME_api=5"
echo "  - Update stack: docker stack deploy -c $COMPOSE_FILE $STACK_NAME"
echo "  - Remove stack: docker stack rm $STACK_NAME"
echo ""
echo "💡 Health checks:"
echo "  - API Health: curl http://localhost/health"
echo "  - Nginx Status: curl http://localhost/nginx-status"
