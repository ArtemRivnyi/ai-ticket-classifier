# 🧪 Testing Commands Guide

## 📋 Table of Contents
1. [Unit Tests](#unit-tests)
2. [API Testing (Classification)](#api-testing-classification)
3. [Prometheus Metrics](#prometheus-metrics)
4. [Grafana Dashboards](#grafana-dashboards)
5. [Health Checks](#health-checks)

---

## 🧪 Unit Tests

### Run All Tests
```bash
# Activate venv (Python 3.12)
source venv/Scripts/activate  # Windows Git Bash
# или
venv\Scripts\activate  # Windows CMD

# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html --cov-report=term-missing

# Quick test (no verbose)
python -m pytest tests/ -q

# Run specific test file
python -m pytest tests/test_app_endpoints.py -v

# Run specific test
python -m pytest tests/test_app_endpoints.py::test_classify_endpoint_all_categories -v
```

### Test Coverage
```bash
# Generate coverage report
python -m pytest tests/ --cov=. --cov-report=html

# View coverage report
# Open htmlcov/index.html in browser
```

---

## 🚀 API Testing (Classification)

### 1. Health Check
```bash
# Check API health
curl http://localhost:5000/api/v1/health

# With formatting
curl http://localhost:5000/api/v1/health | python -m json.tool
```

### 2. Register API Key (First Time)
```bash
# Register new user and get API key
curl -X POST http://localhost:5000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "name": "Test User",
    "organization": "Test Org"
  }' | python -m json.tool

# Save API key from response
export API_KEY="your-api-key-here"
```

**Note:** Registration requires `email`, `name`, and `organization` fields (not `tier`).

### 3. Classify Single Ticket
```bash
# Classify a network issue ticket
curl -X POST http://localhost:5000/api/v1/classify \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "ticket": "I cannot connect to the internet. My WiFi shows connected but no websites load."
  }' | python -m json.tool

# Classify an account problem
curl -X POST http://localhost:5000/api/v1/classify \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "ticket": "I forgot my password and cannot log into my account. Please help me reset it."
  }' | python -m json.tool

# Classify a payment issue
curl -X POST http://localhost:5000/api/v1/classify \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "ticket": "My credit card was charged twice for the subscription. I need a refund."
  }' | python -m json.tool

# Classify a feature request
curl -X POST http://localhost:5000/api/v1/classify \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "ticket": "It would be great if you could add dark mode to the application. Many users have requested this feature."
  }' | python -m json.tool
```

### 4. Batch Classification
```bash
# Classify multiple tickets at once
curl -X POST http://localhost:5000/api/v1/batch \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "tickets": [
      "I cannot access my account",
      "The payment failed with error code 500",
      "Can you add support for mobile app?",
      "Network connection is very slow today"
    ]
  }' | python -m json.tool
```

### 5. Test Different Categories
```bash
# Network Issue
curl -X POST http://localhost:5000/api/v1/classify \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"ticket": "Internet is down, cannot browse websites"}' | python -m json.tool

# Account Problem
curl -X POST http://localhost:5000/api/v1/classify \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"ticket": "Cannot login, password reset not working"}' | python -m json.tool

# Payment Issue
curl -X POST http://localhost:5000/api/v1/classify \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"ticket": "Charged incorrectly, need refund"}' | python -m json.tool

# Feature Request
curl -X POST http://localhost:5000/api/v1/classify \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"ticket": "Please add export to PDF feature"}' | python -m json.tool

# Other
curl -X POST http://localhost:5000/api/v1/classify \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"ticket": "General question about service availability"}' | python -m json.tool
```

### 6. PowerShell Commands (Windows)
```powershell
# Health check
Invoke-RestMethod -Uri "http://localhost:5000/api/v1/health" -Method Get

# Register API key
$body = @{
    email = "test@example.com"
    tier = "professional"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:5000/api/v1/auth/register" -Method Post -Body $body -ContentType "application/json"
$apiKey = $response.api_key

# Classify ticket
$classifyBody = @{
    ticket = "I cannot connect to the internet"
} | ConvertTo-Json

$headers = @{
    "X-API-Key" = $apiKey
}

Invoke-RestMethod -Uri "http://localhost:5000/api/v1/classify" -Method Post -Body $classifyBody -ContentType "application/json" -Headers $headers
```

---

## 📊 Prometheus Metrics

### Access Prometheus UI
```bash
# Open in browser
http://localhost:9090
```

### Query Metrics via API
```bash
# Get all metrics
curl http://localhost:5000/metrics

# Query specific metric in Prometheus
# Open http://localhost:9090/graph
# Then use these queries:

# Total API requests
api_requests_total

# Request duration
api_request_duration_seconds

# Classification count
classifications_total

# API errors
api_errors_total

# Active requests
api_active_requests

# Request rate (last 5 minutes)
rate(api_requests_total[5m])

# Error rate
rate(api_errors_total[5m])

# Average response time
rate(api_request_duration_seconds_sum[5m]) / rate(api_request_duration_seconds_count[5m])
```

### Useful Prometheus Queries
```promql
# Total requests per endpoint
sum by (endpoint) (api_requests_total)

# Request rate by status code
sum by (status) (rate(api_requests_total[5m]))

# P95 response time
histogram_quantile(0.95, rate(api_request_duration_seconds_bucket[5m]))

# Error rate percentage
(rate(api_errors_total[5m]) / rate(api_requests_total[5m])) * 100

# Requests per minute
rate(api_requests_total[1m]) * 60
```

---

## 📈 Grafana Dashboards

### Access Grafana
```bash
# Open in browser
http://localhost:3000

# Default credentials
Username: admin
Password: admin
```

### View Dashboards
1. **Login to Grafana** (http://localhost:3000)
2. **Go to Dashboards** → Browse
3. **Select dashboard**: "AI Ticket Classifier Dashboard"

### Dashboard Panels
- **Total Classifications Rate**: Requests per 5 minutes
- **Classifications by Status**: Success vs Cached
- **Total Classifications Count**: Total number of classifications
- **P95 Response Time**: 95th percentile latency
- **Cache Hit Rate**: Percentage of cached responses
- **API Errors Rate**: Error rate per 5 minutes
- **Classifications by Category**: Distribution by category
- **Average Classification Latency**: Average response time

### Create Custom Queries
```promql
# In Grafana, add new panel with these queries:

# Classification success rate
sum(rate(classifications_total{status="success"}[5m])) / sum(rate(classifications_total[5m])) * 100

# Requests by endpoint
sum by (endpoint) (api_requests_total)

# Error percentage
(sum(rate(api_errors_total[5m])) / sum(rate(api_requests_total[5m]))) * 100
```

---

## 🏥 Health Checks

### Check All Services
```bash
# Check Docker containers
docker-compose ps

# Check application health
curl http://localhost:5000/api/v1/health

# Check Redis
docker exec ai-ticket-redis redis-cli ping

# Check Prometheus
curl http://localhost:9090/-/healthy

# Check Grafana
curl http://localhost:3000/api/health
```

### Check Logs
```bash
# Application logs
docker-compose logs app --tail 50

# All services logs
docker-compose logs --tail 50

# Follow logs
docker-compose logs -f app

# Redis logs
docker-compose logs redis --tail 50
```

---

## 🔄 Generate Test Data for Grafana

### Quick Script
```bash
# Use existing API key
export API_KEY="your-api-key-here"
python generate_test_data.py

# Or let script register new key automatically
python generate_test_data.py
```

This script will:
- Register API key (or use existing from `API_KEY` env var)
- Send 10 single classification requests
- Send 15 batch classification requests
- Generate metrics for Prometheus & Grafana

**After running:**
1. Wait 10-15 seconds
2. Refresh Grafana dashboard
3. Data should appear!

## 🔄 Load Testing

### Generate Test Traffic
```bash
# Run multiple classifications (simple loop)
for i in {1..10}; do
  curl -X POST http://localhost:5000/api/v1/classify \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $API_KEY" \
    -d '{"ticket": "Test ticket number '$i'"}' &
done
wait

# Watch metrics update
watch -n 1 'curl -s http://localhost:5000/metrics | grep api_requests_total'
```

---

## 📝 Quick Test Script

Create `quick_test.sh`:
```bash
#!/bin/bash

API_KEY="your-api-key-here"
BASE_URL="http://localhost:5000"

echo "=== Health Check ==="
curl -s $BASE_URL/api/v1/health | python -m json.tool

echo -e "\n=== Classify Network Issue ==="
curl -s -X POST $BASE_URL/api/v1/classify \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"ticket": "Cannot connect to WiFi"}' | python -m json.tool

echo -e "\n=== Metrics ==="
curl -s $BASE_URL/metrics | grep api_requests_total
```

Make it executable:
```bash
chmod +x quick_test.sh
./quick_test.sh
```

---

## 🎯 Summary

**Quick Commands:**
```bash
# 1. Run tests
python -m pytest tests/ -v

# 2. Test classification
curl -X POST http://localhost:5000/api/v1/classify \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_KEY" \
  -d '{"ticket": "Your ticket text here"}'

# 3. View metrics
curl http://localhost:5000/metrics

# 4. Open Prometheus
# Browser: http://localhost:9090

# 5. Open Grafana
# Browser: http://localhost:3000 (admin/admin)
```

**All services should be running:**
```bash
docker-compose ps
```

