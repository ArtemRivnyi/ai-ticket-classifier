#!/bin/bash

echo "=========================================="
echo "  AI Ticket Classifier - Quick Fix"
echo "=========================================="
echo ""

# Step 1: Stop all containers
echo "Step 1: Stopping containers..."
docker-compose down -v
echo "✓ Done"
echo ""

# Step 2: Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo "Step 2: Creating .env file..."
    cat > .env << 'EOF'
# AI Ticket Classifier - Environment Variables

FLASK_ENV=development
TEST_MODE=true
GEMINI_API_KEY=your_gemini_api_key_here
ADMIN_SECRET=dev_admin_secret_change_in_production_min_32_chars
SECRET_KEY=dev_secret_key_change_in_production_min_32_chars_long
POSTGRES_PASSWORD=postgres
CORS_ORIGINS=http://localhost:3000,http://localhost:5000
FORCE_HTTPS=false
LOG_LEVEL=INFO
EOF
    echo "✓ Created .env file"
else
    echo "Step 2: .env file already exists"
fi
echo ""

# Step 3: Create directories
echo "Step 3: Creating directories..."
mkdir -p data
mkdir -p logs
mkdir -p auth
mkdir -p config
mkdir -p scripts
mkdir -p tests
echo "✓ Done"
echo ""

# Step 4: Build images
echo "Step 4: Building Docker images..."
echo "(This may take a few minutes...)"
docker-compose build --no-cache
echo "✓ Done"
echo ""

# Step 5: Start services
echo "Step 5: Starting services..."
docker-compose up -d
echo "✓ Done"
echo ""

# Step 6: Wait for services to be healthy
echo "Step 6: Waiting for services to be healthy..."
echo "Waiting for Redis..."
for i in {1..30}; do
    if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
        echo "✓ Redis is healthy"
        break
    fi
    sleep 1
done

echo "Waiting for PostgreSQL..."
for i in {1..30}; do
    if docker-compose exec -T db pg_isready -U postgres > /dev/null 2>&1; then
        echo "✓ PostgreSQL is healthy"
        break
    fi
    sleep 1
done

echo "Waiting for Application..."
for i in {1..30}; do
    if curl -sf http://localhost:5000/api/v1/health > /dev/null 2>&1; then
        echo "✓ Application is healthy"
        break
    fi
    sleep 1
done
echo ""

# Step 7: Test
echo "Step 7: Running basic tests..."
echo ""
echo "Test 1: Health check"
curl -s http://localhost:5000/api/v1/health | head -c 100
echo ""
echo ""

echo "Test 2: Info endpoint"
curl -s http://localhost:5000/api/v1/info | head -c 150
echo ""
echo ""

echo "=========================================="
echo "  Setup Complete!"
echo "=========================================="
echo ""
echo "Services running:"
docker-compose ps
echo ""
echo "Next steps:"
echo "1. Set your GEMINI_API_KEY in .env file"
echo "2. Generate API keys: python scripts/generate_api_key.py 'Test User' --tier free"
echo "3. Test API: curl http://localhost:5000/api/v1/health"
echo ""
echo "View logs: docker-compose logs -f"
echo "Stop services: docker-compose down"
echo ""