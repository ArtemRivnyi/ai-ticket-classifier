#!/bin/bash

# AI Ticket Classifier - Quick Start Script
# This script automates the entire setup process

set -e  # Exit on error

echo "🚀 AI Ticket Classifier - Quick Start"
echo "======================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed${NC}"
    echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}✓ Docker found: $(docker --version)${NC}"
echo -e "${GREEN}✓ Docker Compose found: $(docker-compose --version)${NC}"
echo ""

# Check for .env file
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found${NC}"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    
    echo ""
    echo -e "${YELLOW}⚠️  IMPORTANT: Please edit .env and add your API keys${NC}"
    echo ""
    echo "Required:"
    echo "  GEMINI_API_KEY=your_key_here"
    echo ""
    echo "Optional:"
    echo "  OPENAI_API_KEY=your_key_here"
    echo "  REDIS_PASSWORD=your_password"
    echo "  GRAFANA_PASSWORD=your_password"
    echo ""
    read -p "Press Enter after editing .env file..."
fi

# Validate GEMINI_API_KEY
source .env
if [ -z "$GEMINI_API_KEY" ] || [ "$GEMINI_API_KEY" == "your_gemini_api_key_here" ]; then
    echo -e "${RED}❌ GEMINI_API_KEY is not set in .env${NC}"
    echo "Please edit .env and add your Gemini API key"
    echo "Get it from: https://aistudio.google.com/app/apikey"
    exit 1
fi

echo -e "${GREEN}✓ Configuration file ready${NC}"
echo ""

# Stop any running containers
echo "🛑 Stopping any running containers..."
docker-compose down 2>/dev/null || true
echo ""

# Build and start services
echo "🏗️  Building Docker images..."
docker-compose build --no-cache

echo ""
echo "🚀 Starting services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Wait for health check
MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:5000/api/v1/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ API is healthy!${NC}"
        break
    fi
    
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "Waiting for API... ($RETRY_COUNT/$MAX_RETRIES)"
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo -e "${RED}❌ API failed to start${NC}"
    echo "Check logs with: docker-compose logs app"
    exit 1
fi

echo ""
echo "======================================"
echo -e "${GREEN}✅ All services are running!${NC}"
echo "======================================"
echo ""

# Display service URLs
echo "📡 Service URLs:"
echo "  API:        http://localhost:5000"
echo "  Swagger:    http://localhost:5000/api/docs"
echo "  Metrics:    http://localhost:5000/metrics"
echo "  Prometheus: http://localhost:9090"
echo "  Grafana:    http://localhost:3000 (admin/admin)"
echo ""

# Register test user
echo "👤 Registering test user..."
REGISTER_RESPONSE=$(curl -s -X POST http://localhost:5000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "organization": "Test Corp",
    "name": "Test User"
  }')

if [ $? -eq 0 ]; then
    API_KEY=$(echo $REGISTER_RESPONSE | grep -o '"key":"[^"]*"' | cut -d'"' -f4)
    
    if [ -n "$API_KEY" ]; then
        echo -e "${GREEN}✓ Test user registered${NC}"
        echo ""
        echo "======================================"
        echo -e "${YELLOW}🔑 YOUR API KEY (save this!):${NC}"
        echo ""
        echo "  $API_KEY"
        echo ""
        echo "======================================"
        
        # Save to file
        echo "$API_KEY" > .api_key
        chmod 600 .api_key
        echo ""
        echo "API key saved to: .api_key"
        echo ""
        
        # Test classification
        echo "🧪 Testing classification..."
        TEST_RESPONSE=$(curl -s -X POST http://localhost:5000/api/v1/classify \
          -H "Content-Type: application/json" \
          -H "X-API-Key: $API_KEY" \
          -d '{"ticket": "I cannot connect to the VPN"}')
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ Classification test passed${NC}"
            echo ""
            echo "Response:"
            echo "$TEST_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$TEST_RESPONSE"
            echo ""
        else
            echo -e "${YELLOW}⚠️  Classification test failed${NC}"
        fi
    fi
else
    echo -e "${YELLOW}⚠️  Could not register test user${NC}"
    echo "You can register manually:"
    echo ""
    echo 'curl -X POST http://localhost:5000/api/v1/auth/register \'
    echo '  -H "Content-Type: application/json" \'
    echo '  -d '"'"'{"email":"your@email.com","organization":"Your Org","name":"Your Name"}'"'"
    echo ""
fi

# Show useful commands
echo "======================================"
echo "📚 Useful Commands:"
echo "======================================"
echo ""
echo "View logs:"
echo "  docker-compose logs -f app"
echo ""
echo "Restart services:"
echo "  docker-compose restart"
echo ""
echo "Stop services:"
echo "  docker-compose down"
echo ""
echo "Test API:"
echo '  curl -X POST http://localhost:5000/api/v1/classify \'
echo '    -H "Content-Type: application/json" \'
echo "    -H \"X-API-Key: \$(cat .api_key)\" \\"
echo '    -d '"'"'{"ticket":"Cannot connect to VPN"}'"'"
echo ""
echo "======================================"
echo -e "${GREEN}🎉 Setup complete! Happy classifying!${NC}"
echo "======================================"