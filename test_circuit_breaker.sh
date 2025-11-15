#!/bin/bash
API_KEY="093b2dc072107a78d7676dca4cec411fae8e3b2ef80c4dca14a605c116ac1201"

echo "🔴 CIRCUIT BREAKER TEST"
echo "======================"
echo ""
echo "This test simulates provider failure by making invalid requests"
echo ""

# Сделать 10 запросов, чтобы потенциально вызвать ошибки
for i in {1..10}; do
  echo "Request $i:"
  result=$(curl -s -X POST http://localhost:5000/api/v1/classify \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $API_KEY" \
    -d '{"ticket":"test '$i'"}')
  
  provider=$(echo $result | jq -r '.provider // "error"')
  category=$(echo $result | jq -r '.category // "error"')
  
  echo "  ➜ Provider: $provider, Category: $category"
  sleep 1
done

echo ""
echo "📊 Circuit Breaker Status:"
curl -s http://localhost:5000/api/v1/providers/health | jq '.providers[] | {
  name,
  available,
  circuit_state: .circuit_breaker.state,
  failures: .circuit_breaker.failures,
  threshold: .circuit_breaker.threshold
}'

echo ""
echo "✅ Test completed!"
