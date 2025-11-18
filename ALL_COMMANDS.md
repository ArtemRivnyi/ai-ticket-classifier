# 🎯 All Commands - Complete Reference

## ✅ Quick Start

### 1. Start Services
```bash
docker-compose up -d
```

### 2. Generate Test Data for Grafana
```bash
python generate_test_data.py
```

### 3. Open Dashboards
- **Prometheus:** http://localhost:9090
- **Grafana:** http://localhost:3000 (admin/admin)

---

## 🧪 Tests

```bash
# All tests
python -m pytest tests/ -v

# With coverage
python -m pytest tests/ --cov=. --cov-report=html

# Quick test
python -m pytest tests/ -q
```

---

## 🚀 Ticket Classification

### Register API Key
```bash
curl -X POST http://localhost:5000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "name": "Test User",
    "organization": "Test Org"
  }'
```

### Classify Single Ticket
```bash
curl -X POST http://localhost:5000/api/v1/classify \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{"ticket": "I cannot connect to the internet"}'
```

### Batch Classification
```bash
curl -X POST http://localhost:5000/api/v1/batch \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{
    "tickets": [
      "I cannot access my account",
      "Payment failed with error",
      "Please add dark mode"
    ]
  }'
```

### Automatic Data Generation
```bash
# Script will automatically register key and send requests
python generate_test_data.py
```

---

## 📊 Prometheus

### Open UI
```bash
# Browser: http://localhost:9090
```

### Useful Queries
```promql
# Total requests
api_requests_total

# Request rate (per 5 minutes)
rate(api_requests_total[5m])

# Requests by endpoint
sum by (endpoint) (api_requests_total)

# P95 response time
histogram_quantile(0.95, rate(api_request_duration_seconds_bucket[5m]))

# Error percentage
(rate(api_errors_total[5m]) / rate(api_requests_total[5m])) * 100

# Classifications
classifications_total
rate(classifications_total[5m])
```

---

## 📈 Grafana

### Open UI
```bash
# Browser: http://localhost:3000
# Login: admin
# Password: admin
```

### View Dashboard
1. **Dashboards** → **Browse**
2. Select **"AI Ticket Classifier Dashboard"**
3. Set time range: **"Last 5 minutes"**
4. Refresh (F5)

### If "No Data"
1. Run: `python generate_test_data.py`
2. Wait 10-15 seconds
3. Refresh dashboard (F5)

---

## 🔍 Health Checks

### Health Check
```bash
curl http://localhost:5000/api/v1/health
```

### Metrics
```bash
curl http://localhost:5000/metrics
```

### Container Status
```bash
docker-compose ps
```

### Logs
```bash
# Application logs
docker-compose logs app --tail 50

# All logs
docker-compose logs --tail 50
```

---

## 📝 Ready Scripts

### Windows PowerShell
```powershell
.\test_classify.ps1
```

### Linux/Mac
```bash
./test_classify.sh
```

### Python (Universal)
```bash
python generate_test_data.py
```

---

## 🎯 Test Ticket Examples

### Network Issue
```json
{"ticket": "I cannot connect to the internet. WiFi shows connected but no websites load."}
```

### Account Problem
```json
{"ticket": "I forgot my password and cannot log into my account."}
```

### Payment Issue
```json
{"ticket": "My credit card was charged twice. I need a refund."}
```

### Feature Request
```json
{"ticket": "Please add dark mode to the application."}
```

### Other
```json
{"ticket": "General question about service hours."}
```

---

## 📚 Additional Documentation

- **[TESTING_COMMANDS.md](TESTING_COMMANDS.md)** - Complete testing guide
- **[VIEW_METRICS.md](VIEW_METRICS.md)** - Metrics viewing details
- **[QUICK_START_METRICS.md](QUICK_START_METRICS.md)** - Quick start for Grafana

---

## ⚡ Most Important Commands

```bash
# 1. Tests
python -m pytest tests/ -v

# 2. Generate data for Grafana
python generate_test_data.py

# 3. Classify ticket
curl -X POST http://localhost:5000/api/v1/classify \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_KEY" \
  -d '{"ticket": "Your ticket text"}'

# 4. View metrics
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3000
```
