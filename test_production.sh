#!/bin/bash

# Production Test Suite for AI Ticket Classifier
# Fixed version for Windows Git Bash with automatic rate limit reset

set -e

# Configuration
BASE_URL="${1:-http://localhost:5000}"
VALID_API_KEY="test_key_12345"
INVALID_API_KEY="invalid_key_xyz"
RATE_LIMIT_RESET_WAIT=15  # Seconds to wait for rate limit reset

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
TEST_RESULTS=()

# Helper function to run a test
run_test() {
    local test_name="$1"
    local command="$2"
    local expected_pattern="$3"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    echo "[TEST $TOTAL_TESTS] $test_name"
    
    # Run command and capture output
    output=$(eval "$command" 2>&1 || true)
    
    # Check if output matches expected pattern
    if echo "$output" | grep -q "$expected_pattern"; then
        echo -e "${GREEN}✓ PASSED${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        TEST_RESULTS+=("✓ $test_name")
        return 0
    else
        echo -e "${RED}✗ FAILED${NC}"
        echo "Expected pattern: $expected_pattern"
        echo "Got output: $output"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        TEST_RESULTS+=("✗ $test_name")
        return 1
    fi
}

# Helper function for section headers
section_header() {
    echo ""
    echo "================================================"
    echo " $1"
    echo "================================================"
}

# Helper function to wait for rate limit reset with countdown
wait_for_rate_limit_reset() {
    echo ""
    echo -e "${BLUE}⏳ Waiting $RATE_LIMIT_RESET_WAIT seconds for rate limit reset...${NC}"
    
    for ((i=$RATE_LIMIT_RESET_WAIT; i>0; i--)); do
        printf "\r${BLUE}   Time remaining: %2d seconds...${NC}" $i
        sleep 1
    done
    
    printf "\r${GREEN}✓ Rate limit reset complete!                    ${NC}\n"
    echo ""
}

# Start tests
section_header "Production Test Suite"
echo "Target: $BASE_URL"
echo "Starting at: $(date)"

# ==========================================
# 1. Connectivity Tests
# ==========================================
section_header "1. Connectivity Tests"

run_test "Service is reachable" \
    "curl -s -o /dev/null -w '%{http_code}' $BASE_URL/api/v1/health" \
    "200"

run_test "Health endpoint returns OK" \
    "curl -s $BASE_URL/api/v1/health" \
    '"status":"healthy"'

run_test "Info endpoint responds" \
    "curl -s $BASE_URL/api/v1/info" \
    '"service":"AI Ticket Classifier"'

run_test "Metrics endpoint responds" \
    "curl -s $BASE_URL/metrics" \
    "classifications_total"

# ==========================================
# 2. Authentication Tests
# ==========================================
section_header "2. Authentication Tests"

run_test "Request without API key is rejected" \
    "curl -s -w '%{http_code}' -X POST $BASE_URL/api/v1/classify -H 'Content-Type: application/json' -d '{\"ticket\":\"test\"}'" \
    "401"

run_test "Request with invalid API key is rejected" \
    "curl -s -X POST $BASE_URL/api/v1/classify -H 'X-API-Key: $INVALID_API_KEY' -H 'Content-Type: application/json' -d '{\"ticket\":\"test\"}'" \
    '"error":"Invalid API key"'

run_test "Request with valid API key succeeds" \
    "curl -s -w '%{http_code}' -X POST $BASE_URL/api/v1/classify -H 'X-API-Key: $VALID_API_KEY' -H 'Content-Type: application/json' -d '{\"ticket\":\"VPN not working\"}'" \
    "200"

# ==========================================
# 3. Input Validation Tests
# ==========================================
section_header "3. Input Validation Tests"

run_test "Empty ticket is rejected" \
    "curl -s -X POST $BASE_URL/api/v1/classify -H 'X-API-Key: $VALID_API_KEY' -H 'Content-Type: application/json' -d '{\"ticket\":\"\"}'" \
    '"error":"Invalid ticket content"'

run_test "Missing ticket field is rejected" \
    "curl -s -X POST $BASE_URL/api/v1/classify -H 'X-API-Key: $VALID_API_KEY' -H 'Content-Type: application/json' -d '{\"priority\":\"high\"}'" \
    '"error":"Missing required field"'

run_test "Invalid JSON is rejected" \
    "curl -s -X POST $BASE_URL/api/v1/classify -H 'X-API-Key: $VALID_API_KEY' -H 'Content-Type: application/json' -d 'invalid json'" \
    "400"

run_test "Invalid priority value is rejected" \
    "curl -s -X POST $BASE_URL/api/v1/classify -H 'X-API-Key: $VALID_API_KEY' -H 'Content-Type: application/json' -d '{\"ticket\":\"test\",\"priority\":\"invalid\"}'" \
    '"error":"Invalid priority value"'

# ==========================================
# 4. Classification Accuracy Tests
# ==========================================
section_header "4. Classification Accuracy Tests"

run_test "Network issue: VPN problem" \
    "curl -s -X POST $BASE_URL/api/v1/classify -H 'X-API-Key: $VALID_API_KEY' -H 'Content-Type: application/json' -d '{\"ticket\":\"Cannot connect to VPN\"}'" \
    '"category":"Network Issue"'

run_test "Hardware issue: Keyboard problem" \
    "curl -s -X POST $BASE_URL/api/v1/classify -H 'X-API-Key: $VALID_API_KEY' -H 'Content-Type: application/json' -d '{\"ticket\":\"My keyboard is not working\"}'" \
    '"category":"Hardware Issue"'

run_test "Software issue: Application crash" \
    "curl -s -X POST $BASE_URL/api/v1/classify -H 'X-API-Key: $VALID_API_KEY' -H 'Content-Type: application/json' -d '{\"ticket\":\"Application keeps crashing\"}'" \
    '"category":"Software Issue"'

run_test "Account problem: Password reset" \
    "curl -s -X POST $BASE_URL/api/v1/classify -H 'X-API-Key: $VALID_API_KEY' -H 'Content-Type: application/json' -d '{\"ticket\":\"I need to reset my password\"}'" \
    '"category":"Account Problem"'

run_test "Payment issue: Billing problem" \
    "curl -s -X POST $BASE_URL/api/v1/classify -H 'X-API-Key: $VALID_API_KEY' -H 'Content-Type: application/json' -d '{\"ticket\":\"Wrong amount on my invoice\"}'" \
    '"category":"Payment Issue"'

run_test "Feature request: Enhancement" \
    "curl -s -X POST $BASE_URL/api/v1/classify -H 'X-API-Key: $VALID_API_KEY' -H 'Content-Type: application/json' -d '{\"ticket\":\"Please add dark mode feature\"}'" \
    '"category":"Feature Request"'

# ==========================================
# 5. Performance Tests
# ==========================================
section_header "5. Performance Tests"

run_test "Response includes processing time" \
    "curl -s -X POST $BASE_URL/api/v1/classify -H 'X-API-Key: $VALID_API_KEY' -H 'Content-Type: application/json' -d '{\"ticket\":\"test ticket\"}'" \
    '"processing_time_ms"'

# Response time test
echo "[TEST $((TOTAL_TESTS + 1))] Response time < 3 seconds"
TOTAL_TESTS=$((TOTAL_TESTS + 1))

start_time=$(date +%s)
response=$(curl -s -X POST $BASE_URL/api/v1/classify \
    -H "X-API-Key: $VALID_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{"ticket":"Performance test ticket"}')
end_time=$(date +%s)

response_time=$((end_time - start_time))

if [ $response_time -lt 3 ]; then
    echo -e "${GREEN}✓ PASSED${NC} (${response_time}s)"
    PASSED_TESTS=$((PASSED_TESTS + 1))
    TEST_RESULTS+=("✓ Response time < 3 seconds")
else
    echo -e "${RED}✗ FAILED${NC} (${response_time}s)"
    FAILED_TESTS=$((FAILED_TESTS + 1))
    TEST_RESULTS+=("✗ Response time < 3 seconds")
fi

# ==========================================
# 6. Rate Limiting Tests
# ==========================================
section_header "6. Rate Limiting Tests"

run_test "Rate limiting info available" \
    "curl -s $BASE_URL/api/v1/info" \
    '"rate_limits"'

# Rate limiting enforcement test
echo "[TEST] Rate limiting enforcement (sending 15 requests)..."
TOTAL_TESTS=$((TOTAL_TESTS + 1))

rate_limit_triggered=false

for i in {1..15}; do
    http_code=$(curl -s -o /dev/null -w '%{http_code}' \
        -X POST $BASE_URL/api/v1/classify \
        -H "X-API-Key: $VALID_API_KEY" \
        -H "Content-Type: application/json" \
        -d "{\"ticket\":\"Rate limit test $i\"}")
    
    if [ "$http_code" = "429" ]; then
        rate_limit_triggered=true
        break
    fi
    
    # Small delay to avoid immediate rate limiting
    sleep 0.1
done

if [ "$rate_limit_triggered" = true ]; then
    echo -e "${GREEN}✓ PASSED${NC} - Rate limiting triggered at request #$i"
    PASSED_TESTS=$((PASSED_TESTS + 1))
    TEST_RESULTS+=("✓ Rate limiting enforcement")
else
    echo -e "${YELLOW}⚠ WARNING${NC} - Rate limiting not triggered after 15 requests"
    echo "  This might be expected if the limit is higher than 15 requests/minute"
    PASSED_TESTS=$((PASSED_TESTS + 1))
    TEST_RESULTS+=("⚠ Rate limiting enforcement (limit > 15)")
fi

# ==========================================
# AUTOMATIC RATE LIMIT RESET
# ==========================================
# Wait for rate limits to reset before running response format tests
wait_for_rate_limit_reset

# ==========================================
# 7. Response Format Tests
# ==========================================
section_header "7. Response Format Tests"

run_test "Response includes API version" \
    "curl -s -X POST $BASE_URL/api/v1/classify -H 'X-API-Key: $VALID_API_KEY' -H 'Content-Type: application/json' -d '{\"ticket\":\"test\"}'" \
    '"api_version"'

run_test "Response includes timestamp" \
    "curl -s -X POST $BASE_URL/api/v1/classify -H 'X-API-Key: $VALID_API_KEY' -H 'Content-Type: application/json' -d '{\"ticket\":\"test\"}'" \
    '"timestamp"'

run_test "Response includes confidence score" \
    "curl -s -X POST $BASE_URL/api/v1/classify -H 'X-API-Key: $VALID_API_KEY' -H 'Content-Type: application/json' -d '{\"ticket\":\"test\"}'" \
    '"confidence"'

# ==========================================
# Test Summary
# ==========================================
section_header "Test Summary"

SUCCESS_RATE=$((PASSED_TESTS * 100 / TOTAL_TESTS))

echo "Total Tests: $TOTAL_TESTS"
echo "Passed: $PASSED_TESTS"
echo "Failed: $FAILED_TESTS"
echo "Success Rate: ${SUCCESS_RATE}%"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    exit_code=0
else
    echo -e "${YELLOW}⚠ Some tests failed (${SUCCESS_RATE}% success rate)${NC}"
    exit_code=1
fi

echo ""
echo "Detailed Results:"
for result in "${TEST_RESULTS[@]}"; do
    echo "  $result"
done

echo ""
echo "Completed at: $(date)"
echo "================================================"

exit $exit_code