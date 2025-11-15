# Упрощённая версия теста без jq
cat > test_production_simple.sh << 'EOF'
#!/bin/bash

API_KEY="093b2dc072107a78d7676dca4cec411fae8e3b2ef80c4dca14a605c116ac1201"
BASE_URL="http://localhost:5000"

echo "======================================"
echo "🚀 AI TICKET CLASSIFIER - PRODUCTION TEST"
echo "======================================"
echo ""

# 1. Health Check
echo "1️⃣ Health Check:"
curl -s $BASE_URL/api/v1/health
echo -e "\n"

# 2. Info
echo "2️⃣ API Info:"
curl -s $BASE_URL/api/v1/info
echo -e "\n"

# 3. Classifications
echo "3️⃣ Testing Classifications..."
echo ""

echo "Test 1: Hardware Issue"
curl -s -X POST $BASE_URL/api/v1/classify \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"ticket": "My laptop keyboard is broken"}'
echo -e "\n"

echo "Test 2: Network Issue"
curl -s -X POST $BASE_URL/api/v1/classify \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"ticket": "Cannot connect to VPN"}'
echo -e "\n"

echo "Test 3: Software Issue"
curl -s -X POST $BASE_URL/api/v1/classify \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"ticket": "Word keeps crashing"}'
echo -e "\n"

echo "Test 4: Account Problem"
curl -s -X POST $BASE_URL/api/v1/classify \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"ticket": "Forgot my password"}'
echo -e "\n"

echo "Test 5: Payment Issue"
curl -s -X POST $BASE_URL/api/v1/classify \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"ticket": "Was charged twice"}'
echo -e "\n"

# 4. Cache Test (repeat first request)
echo "4️⃣ Cache Test (repeat first request):"
curl -s -X POST $BASE_URL/api/v1/classify \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"ticket": "My laptop keyboard is broken"}'
echo -e "\n"

# 5. Cache Stats
echo "5️⃣ Cache Statistics:"
curl -s $BASE_URL/api/v1/cache/stats -H "X-API-Key: $API_KEY"
echo -e "\n"

# 6. Prometheus Metrics
echo "6️⃣ Prometheus Metrics Sample:"
curl -s $BASE_URL/metrics | grep -E "classifications_total|cache_hits"
echo ""

echo "======================================"
echo "✅ TEST COMPLETE"
echo "======================================"
echo ""
echo "📊 Access Points:"
echo "  • API:        http://localhost:5000"
echo "  • Grafana:    http://localhost:3000 (admin/admin123)"
echo "  • Prometheus: http://localhost:9090"
EOF

chmod +x test_production_simple.sh
./test_production_simple.sh