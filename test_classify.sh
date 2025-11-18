#!/bin/bash
# Bash script for testing ticket classification
# Usage: ./test_classify.sh

BASE_URL="http://localhost:5000"

echo "=== Registering new user ==="
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "tier": "professional"
  }')

API_KEY=$(echo $REGISTER_RESPONSE | python -c "import sys, json; print(json.load(sys.stdin)['api_key'])")
echo "API Key: $API_KEY"
echo ""

# Test tickets
echo "=== Testing Classification ==="
echo ""

test_ticket() {
    local ticket="$1"
    local expected="$2"
    
    echo "Ticket: $ticket"
    echo "Expected: $expected"
    
    RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/classify" \
      -H "Content-Type: application/json" \
      -H "X-API-Key: $API_KEY" \
      -d "{\"ticket\": \"$ticket\"}")
    
    CATEGORY=$(echo $RESPONSE | python -c "import sys, json; print(json.load(sys.stdin)['category'])")
    CONFIDENCE=$(echo $RESPONSE | python -c "import sys, json; print(json.load(sys.stdin)['confidence'])")
    PROVIDER=$(echo $RESPONSE | python -c "import sys, json; print(json.load(sys.stdin)['provider'])")
    
    echo "Result: $CATEGORY"
    echo "Confidence: $CONFIDENCE"
    echo "Provider: $PROVIDER"
    
    if [ "$CATEGORY" == "$expected" ]; then
        echo "✓ Correct!"
    else
        echo "✗ Mismatch"
    fi
    echo ""
    sleep 1
}

# Run tests
test_ticket "I cannot connect to the internet. WiFi shows connected but no websites load." "Network Issue"
test_ticket "I forgot my password and cannot log into my account." "Account Problem"
test_ticket "My credit card was charged twice. I need a refund." "Payment Issue"
test_ticket "Please add dark mode to the application." "Feature Request"
test_ticket "General question about service hours." "Other"

echo "=== Health Check ==="
curl -s "$BASE_URL/api/v1/health" | python -m json.tool
echo ""

echo "=== Metrics Summary ==="
curl -s "$BASE_URL/metrics" | grep "api_requests_total" | head -5
echo ""

echo "✓ Testing complete!"
echo ""
echo "View metrics at: http://localhost:9090"
echo "View dashboards at: http://localhost:3000"

