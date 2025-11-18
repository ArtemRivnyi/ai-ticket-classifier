# 📊 Viewing Metrics in Prometheus & Grafana

## 🎯 Quick Start

### 1. Generate Test Data
```bash
# Generate test classification requests
python generate_test_data.py
```

### 2. View Prometheus
```bash
# Open in browser
http://localhost:9090
```

### 3. View Grafana
```bash
# Open in browser
http://localhost:3000
# Login: admin / admin
```

---

## 📈 Prometheus Queries

### Basic Metrics
```promql
# Total API requests
api_requests_total

# Request rate (per 5 minutes)
rate(api_requests_total[5m])

# Requests by endpoint
sum by (endpoint) (api_requests_total)

# Requests by status code
sum by (status) (api_requests_total)
```

### Performance Metrics
```promql
# Average response time
rate(api_request_duration_seconds_sum[5m]) / rate(api_request_duration_seconds_count[5m])

# P95 response time
histogram_quantile(0.95, rate(api_request_duration_seconds_bucket[5m]))

# P99 response time
histogram_quantile(0.99, rate(api_request_duration_seconds_bucket[5m]))
```

### Error Metrics
```promql
# Error rate
rate(api_errors_total[5m])

# Error percentage
(rate(api_errors_total[5m]) / rate(api_requests_total[5m])) * 100

# Errors by endpoint
sum by (endpoint) (rate(api_errors_total[5m]))
```

### Classification Metrics
```promql
# Total classifications
classifications_total

# Classification rate
rate(classifications_total[5m])

# Classifications by status
sum by (status) (classifications_total)
```

---

## 📊 Grafana Dashboard

### Access Dashboard
1. Open http://localhost:3000
2. Login: `admin` / `admin`
3. Go to **Dashboards** → **Browse**
4. Select **"AI Ticket Classifier Dashboard"**

### Dashboard Panels

#### Row 1: Overview
- **Total Classifications Rate**: Requests per 5 minutes
- **Classifications by Status**: Success vs Cached

#### Row 2: Key Metrics
- **Total Classifications**: Total count
- **P95 Response Time**: 95th percentile latency
- **Cache Hit Rate**: Percentage of cached responses
- **API Errors Rate**: Error rate per 5 minutes

#### Row 3: Analysis
- **Classifications by Category**: Distribution by category
- **Average Classification Latency**: Average response time

### If Dashboard Shows "No Data"

1. **Generate test data:**
   ```bash
   python generate_test_data.py
   ```

2. **Wait 10-15 seconds** for metrics to propagate

3. **Refresh Grafana dashboard** (F5 or refresh button)

4. **Check time range** in Grafana:
   - Click time selector (top right)
   - Select "Last 5 minutes" or "Last 15 minutes"

5. **Verify Prometheus is scraping:**
   ```bash
   # Check Prometheus targets
   http://localhost:9090/targets
   ```
   Should show `ai-ticket-classifier:5000` as UP

---

## 🔍 Troubleshooting

### No Data in Grafana

**Problem:** Dashboard shows "No data"

**Solutions:**
1. Generate test requests:
   ```bash
   python generate_test_data.py
   ```

2. Check Prometheus has data:
   ```bash
   # In Prometheus, query:
   api_requests_total
   ```
   Should return results

3. Check Prometheus targets:
   ```bash
   # Open http://localhost:9090/targets
   # Verify ai-ticket-classifier:5000 is UP
   ```

4. Check time range in Grafana:
   - Make sure it's set to "Last 5 minutes" or recent time

5. Restart services:
   ```bash
   docker-compose restart prometheus grafana
   ```

### Prometheus Not Scraping

**Problem:** Prometheus shows target as DOWN

**Solutions:**
1. Check application is running:
   ```bash
   docker-compose ps
   curl http://localhost:5000/metrics
   ```

2. Check Prometheus config:
   ```bash
   docker-compose logs prometheus
   ```

3. Restart Prometheus:
   ```bash
   docker-compose restart prometheus
   ```

---

## 🧪 Continuous Testing

### Generate Continuous Load
```bash
# Run test script multiple times
for i in {1..5}; do
  echo "Run $i..."
  python generate_test_data.py
  sleep 10
done
```

### Monitor in Real-Time
1. Open Grafana dashboard
2. Set refresh to "5s" (top right)
3. Watch metrics update in real-time

---

## 📝 Quick Reference

**URLs:**
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000
- Metrics API: http://localhost:5000/metrics
- Health: http://localhost:5000/api/v1/health

**Useful Prometheus Queries:**
```promql
# Request rate
rate(api_requests_total[5m])

# Error rate
rate(api_errors_total[5m])

# P95 latency
histogram_quantile(0.95, rate(api_request_duration_seconds_bucket[5m]))
```

**Generate Test Data:**
```bash
python generate_test_data.py
```

