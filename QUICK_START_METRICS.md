# ⚡ Quick Start: View Metrics in Grafana

## 🎯 Problem: Grafana Shows "No Data"

**Solution:** Generate test data first!

## 📝 Step-by-Step

### 1. Generate Test Data
```bash
# Option A: Use your existing API key (if valid)
export API_KEY="your-api-key-here"
python generate_test_data.py

# Option B: Let script register new key automatically (RECOMMENDED)
python generate_test_data.py
```

**The script will:**
- Automatically register a new user with unique email
- Get API key from registration
- Send 10 single classification requests
- Send batch classification requests
- Generate metrics for Prometheus & Grafana

### 2. Wait 10-15 seconds
Metrics need time to propagate from application → Prometheus → Grafana

### 3. Refresh Grafana Dashboard
- Open http://localhost:3000
- Go to **Dashboards** → **Browse**
- Select **"AI Ticket Classifier Dashboard"**
- Click **Refresh** button (top right) or press **F5**

### 4. Check Time Range
- Click time selector (top right)
- Select **"Last 5 minutes"** or **"Last 15 minutes"**

## ✅ Expected Result

After generating test data, you should see:
- ✅ Total Classifications Rate (graph)
- ✅ Classifications by Status (pie chart)
- ✅ Total Classifications Count (number)
- ✅ P95 Response Time (number)
- ✅ Cache Hit Rate (number)
- ✅ API Errors Rate (number)
- ✅ Classifications by Category (bar chart)
- ✅ Average Classification Latency (graph)

## 🔍 Troubleshooting

### Still No Data?

1. **Check Prometheus has data:**
   ```bash
   # Open http://localhost:9090
   # Query: api_requests_total
   # Should return results
   ```

2. **Check Prometheus targets:**
   ```bash
   # Open http://localhost:9090/targets
   # Verify: ai-ticket-classifier:5000 is UP
   ```

3. **Restart services:**
   ```bash
   docker-compose restart prometheus grafana
   ```

4. **Generate more data:**
   ```bash
   # Run multiple times
   for i in {1..3}; do
     python generate_test_data.py
     sleep 5
   done
   ```

## 📊 Quick Commands

```bash
# 1. Generate test data
python generate_test_data.py

# 2. View Prometheus
# Browser: http://localhost:9090

# 3. View Grafana  
# Browser: http://localhost:3000 (admin/admin)

# 4. Check metrics API
curl http://localhost:5000/metrics | grep api_requests_total
```

## 💡 Tips

- **Auto-refresh:** Set Grafana refresh to "5s" (top right)
- **Time range:** Use "Last 5 minutes" for recent data
- **More data:** Run `generate_test_data.py` multiple times
- **Real-time:** Keep script running in loop for continuous metrics

