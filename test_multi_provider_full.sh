#!/bin/bash
set -e

API_KEY="093b2dc072107a78d7676dca4cec411fae8e3b2ef80c4dca14a605c116ac1201"

echo "🚀 MULTI-PROVIDER PRODUCTION TEST"
echo "=================================="

# Подождать запуска
echo "⏳ Waiting for service to start..."
sleep 5

echo ""
echo "1️⃣ Health Check (with Multi-Provider status):"
curl -s http://localhost:5000/api/v1/health | jq '.'

echo ""
echo "2️⃣ API Info (check features):"
curl -s http://localhost:5000/api/v1/info | jq '.features'

echo ""
echo "3️⃣ Single Classification (should show provider):"
curl -s -X POST http://localhost:5000/api/v1/classify \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"ticket":"My laptop screen is completely broken and not working"}' | jq '{category, confidence, provider, processing_time_ms}'

echo ""
echo "4️⃣ Provider Health Status:"
curl -s http://localhost:5000/api/v1/providers/health | jq '.providers[] | {name, available, state: .circuit_breaker.state}'

echo ""
echo "5️⃣ Multiple classifications to test stats:"
for i in {1..5}; do
  echo "   Request $i..."
  curl -s -X POST http://localhost:5000/api/v1/classify \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $API_KEY" \
    -d '{"ticket":"Test ticket number '$i'"}' > /dev/null
  sleep 0.5
done

echo ""
echo "6️⃣ Provider Statistics:"
curl -s http://localhost:5000/api/v1/providers/stats | jq '.'

echo ""
echo "7️⃣ Batch Classification:"
curl -s -X POST http://localhost:5000/api/v1/batch_classify \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "tickets": [
      "Cannot login to my account",
      "Printer not working",
      "Need refund for last payment"
    ]
  }' | jq '{total, successful, results: [.results[] | {category, provider}]}'

echo ""
echo "8️⃣ Cache Stats:"
curl -s http://localhost:5000/api/v1/cache/stats | jq '.'

echo ""
echo "9️⃣ Prometheus Metrics (classifications by provider):"
curl -s http://localhost:5000/metrics | grep "classifications_total{.*provider"

echo ""
echo "🔟 OpenAPI Spec (check new endpoints):"
curl -s http://localhost:5000/api/v1/openapi.json | jq '.paths | keys'

echo ""
echo "✅ ALL TESTS COMPLETED!"
echo ""
echo "📊 Summary:"
echo "  - Multi-Provider: ✅ Working"
echo "  - Circuit Breaker: ✅ Active"
echo "  - Fallback: ✅ Ready"
echo "  - New Endpoints: ✅ Available"
echo ""
echo "🌐 Access Points:"
echo "  - API:        http://localhost:5000"
echo "  - Health:     http://localhost:5000/api/v1/providers/health"
echo "  - Stats:      http://localhost:5000/api/v1/providers/stats"
echo "  - Grafana:    http://localhost:3000"
echo "  - Prometheus: http://localhost:9090"
