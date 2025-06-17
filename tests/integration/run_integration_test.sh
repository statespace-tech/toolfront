#!/bin/bash
set -e

echo "🚀 Starting SSH Tunneling Integration Test"
echo "=========================================="

# Clean up any existing containers
echo "🧹 Cleaning up existing containers..."
docker-compose -f docker-compose.integration.yml down -v --remove-orphans

# Build and start services
echo "🏗️  Building and starting services..."
docker-compose -f docker-compose.integration.yml up -d --build

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check service health
echo "🔍 Checking service health..."
docker-compose -f docker-compose.integration.yml ps

# Wait for SSH bastion to be fully ready
echo "⏳ Waiting for SSH bastion to be ready..."
timeout 60 bash -c 'until docker-compose -f docker-compose.integration.yml exec -T ssh-bastion nc -z localhost 2222; do sleep 2; done'

# Wait for PostgreSQL to be fully ready
echo "⏳ Waiting for PostgreSQL to be ready..."
timeout 60 bash -c 'until docker-compose -f docker-compose.integration.yml exec -T postgres-private pg_isready -U testuser -d testdb; do sleep 2; done'

echo "✅ All services are ready!"

# Run the integration tests
echo "🧪 Running SSH tunneling integration tests..."
docker-compose -f docker-compose.integration.yml run --rm test-runner

echo "🎉 Integration tests completed!"

# Clean up
echo "🧹 Cleaning up..."
docker-compose -f docker-compose.integration.yml down -v

echo "✅ SSH Tunneling Integration Test Complete!"
echo "✅ Tejas's use case is fully supported!"