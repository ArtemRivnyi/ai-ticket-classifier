#!/bin/bash

# ==============================================
# AI Ticket Classifier - Production Deployment
# ==============================================
#
# Usage:
#   ./deploy.sh [environment]
#
# Environments: dev, staging, production
# Default: production
#
# ==============================================

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT="${1:-production}"
PROJECT_NAME="ai-ticket-classifier"
BACKUP_DIR="./backups"
LOG_FILE="./deploy-$(date +%Y%m%d-%H%M%S).log"

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

# Error handler
handle_error() {
    log_error "Deployment failed at line $1"
    log_error "Check $LOG_FILE for details"
    exit 1
}

trap 'handle_error $LINENO' ERR

# Header
echo "================================================"
echo " AI Ticket Classifier - Production Deployment  "
echo "================================================"
echo ""
log_info "Environment: $ENVIRONMENT"
log_info "Started at: $(date)"
echo ""

# Step 1: Pre-flight checks
log_info "Step 1/10: Running pre-flight checks..."

# Check if required commands exist
for cmd in docker docker-compose git curl; do
    if ! command -v $cmd &> /dev/null; then
        log_error "$cmd is not installed"
        exit 1
    fi
done
log_success "All required commands available"

# Check if .env exists
if [ ! -f .env ]; then
    log_error ".env file not found!"
    log_error "Copy .env.example to .env and configure it"
    exit 1
fi
log_success ".env file exists"

# Check if required environment variables are set
source .env
if [ -z "$GEMINI_API_KEY" ] || [ -z "$API_KEY" ]; then
    log_error "Required environment variables not set in .env"
    exit 1
fi
log_success "Environment variables configured"

# Step 2: Create backup
log_info "Step 2/10: Creating backup..."
mkdir -p "$BACKUP_DIR"
BACKUP_NAME="$PROJECT_NAME-$(date +%Y%m%d-%H%M%S).tar.gz"

if [ -d "logs" ]; then
    tar -czf "$BACKUP_DIR/$BACKUP_NAME" logs/ .env 2>/dev/null || true
    log_success "Backup created: $BACKUP_DIR/$BACKUP_NAME"
else
    log_warning "No logs directory to backup"
fi

# Step 3: Pull latest code (if in git repo)
if [ -d ".git" ]; then
    log_info "Step 3/10: Pulling latest code..."
    git fetch origin
    CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
    log_info "Current branch: $CURRENT_BRANCH"
    
    # Check for uncommitted changes
    if ! git diff-index --quiet HEAD --; then
        log_warning "Uncommitted changes detected!"
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_error "Deployment cancelled by user"
            exit 1
        fi
    fi
    
    # Pull latest changes
    git pull origin "$CURRENT_BRANCH"
    log_success "Code updated to latest version"
else
    log_warning "Not a git repository, skipping code pull"
fi

# Step 4: Run tests
log_info "Step 4/10: Running tests..."
if command -v python3 &> /dev/null; then
    if [ -f "requirements.txt" ]; then
        log_info "Installing/updating dependencies..."
        python3 -m pip install -q -r requirements.txt
    fi
    
    if [ -f "test_app.py" ]; then
        log_info "Running test suite..."
        python3 -m pytest test_app.py -v --tb=short || {
            log_error "Tests failed!"
            read -p "Deploy anyway? (y/N) " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                exit 1
            fi
        }
        log_success "Tests passed"
    else
        log_warning "No tests found"
    fi
else
    log_warning "Python3 not available, skipping tests"
fi

# Step 5: Build Docker image
log_info "Step 5/10: Building Docker image..."
docker compose build --no-cache
log_success "Docker image built successfully"

# Step 6: Stop existing containers gracefully
log_info "Step 6/10: Stopping existing containers..."
if docker compose ps | grep -q "$PROJECT_NAME"; then
    log_info "Gracefully stopping containers..."
    docker compose down --timeout 30
    log_success "Containers stopped"
else
    log_info "No running containers to stop"
fi

# Step 7: Start new containers
log_info "Step 7/10: Starting new containers..."
docker compose up -d
log_success "Containers started"

# Step 8: Wait for health check
log_info "Step 8/10: Waiting for service to be healthy..."
MAX_RETRIES=30
RETRY_COUNT=0
HEALTH_ENDPOINT="http://localhost:5000/api/v1/health"

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -sf "$HEALTH_ENDPOINT" > /dev/null 2>&1; then
        log_success "Service is healthy!"
        break
    fi
    
    RETRY_COUNT=$((RETRY_COUNT + 1))
    log_info "Waiting for service... ($RETRY_COUNT/$MAX_RETRIES)"
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    log_error "Service failed to start within timeout"
    log_error "Check logs with: docker compose logs"
    exit 1
fi

# Step 9: Run smoke tests
log_info "Step 9/10: Running smoke tests..."

# Test 1: Health endpoint
log_info "Testing health endpoint..."
HEALTH_RESPONSE=$(curl -sf "$HEALTH_ENDPOINT")
if echo "$HEALTH_RESPONSE" | grep -q '"status":"ok"'; then
    log_success "Health check passed"
else
    log_error "Health check failed"
    exit 1
fi

# Test 2: Info endpoint
log_info "Testing info endpoint..."
INFO_RESPONSE=$(curl -sf "http://localhost:5000/api/v1/info")
if echo "$INFO_RESPONSE" | grep -q '"service":"AI Ticket Classifier"'; then
    log_success "Info endpoint passed"
else
    log_error "Info endpoint failed"
    exit 1
fi

# Test 3: Classification endpoint
log_info "Testing classification endpoint..."
CLASSIFY_RESPONSE=$(curl -sf -X POST "http://localhost:5000/api/v1/classify" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $API_KEY" \
    -d '{"ticket":"Test VPN connection issue"}')

if echo "$CLASSIFY_RESPONSE" | grep -q '"category"'; then
    log_success "Classification endpoint passed"
else
    log_error "Classification endpoint failed"
    exit 1
fi

log_success "All smoke tests passed!"

# Step 10: Display summary
log_info "Step 10/10: Deployment summary"
echo ""
echo "================================================"
echo " Deployment Summary"
echo "================================================"
echo ""
echo "Status: ${GREEN}SUCCESS${NC}"
echo "Environment: $ENVIRONMENT"
echo "Completed at: $(date)"
echo ""
echo "Container Status:"
docker compose ps
echo ""
echo "Endpoints:"
echo "  - Health: http://localhost:5000/api/v1/health"
echo "  - Info: http://localhost:5000/api/v1/info"
echo "  - Classify: http://localhost:5000/api/v1/classify"
echo "  - Metrics: http://localhost:5000/metrics"
echo ""
echo "Quick Commands:"
echo "  - View logs: docker compose logs -f"
echo "  - Stop service: docker compose down"
echo "  - Restart service: docker compose restart"
echo ""
echo "Backup location: $BACKUP_DIR/$BACKUP_NAME"
echo "Log file: $LOG_FILE"
echo ""
echo "================================================"
echo ""

log_success "Deployment completed successfully!"

# Optional: Send notification (uncomment and configure)
# curl -X POST "https://your-webhook-url.com" \
#     -H "Content-Type: application/json" \
#     -d "{\"text\":\"✅ $PROJECT_NAME deployed successfully to $ENVIRONMENT\"}"