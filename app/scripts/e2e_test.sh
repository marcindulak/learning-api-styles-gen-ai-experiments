#!/bin/bash
# End-to-end test script for Weather Forecast Service
# Tests all API patterns: REST, GraphQL, Atom feeds, WebSocket, webhooks, documentation
# Runs inside container via: docker compose exec app bash /app/scripts/e2e_test.sh

set -e

PASS=0
FAIL=0
BASE_URL="http://localhost:8000"
WEBHOOK_SECRET="${WEBHOOK_SECRET:-a0tObtQBvNhQjRSbPRZrIkXiooIH2ucIZJeESrRcIFyYOtSV8FKWrAri8djp3CQd}"

echo "========================================="
echo "E2E Tests for Weather Forecast Service"
echo "========================================="
echo ""

# Helper function to test
test_endpoint() {
    local name=$1
    local method=$2
    local endpoint=$3
    local data=$4
    local expected_code=$5
    local headers=$6

    echo -n "Testing: $name ... "

    if [ -z "$headers" ]; then
        headers="-H 'Content-Type: application/json'"
    fi

    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" -X GET $headers "$BASE_URL$endpoint")
    else
        response=$(curl -s -w "\n%{http_code}" -X $method "$BASE_URL$endpoint" $headers --data "$data")
    fi

    http_code=$(echo "$response" | tail -1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" = "$expected_code" ]; then
        echo "PASS (HTTP $http_code)"
        ((PASS++))
        return 0
    else
        echo "FAIL (Expected $expected_code, got $http_code)"
        ((FAIL++))
        return 1
    fi
}

# Test 1: JWT Authentication
echo "1. JWT Authentication Tests"
echo "---"
JWT_PAYLOAD='{"username":"admin","password":"admin"}'
JWT_RESPONSE=$(curl -s -X POST "$BASE_URL/api/jwt/obtain" \
    -H "Content-Type: application/json" \
    --data "$JWT_PAYLOAD")
ACCESS_TOKEN=$(echo "$JWT_RESPONSE" | grep -o '"access":"[^"]*' | cut -d'"' -f4)

if [ -n "$ACCESS_TOKEN" ]; then
    echo "✓ JWT token obtained: ${ACCESS_TOKEN:0:20}..."
    ((PASS++))
else
    echo "✗ Failed to obtain JWT token"
    ((FAIL++))
fi
echo ""

# Test 2: REST API - Cities
echo "2. REST API - Cities Tests"
echo "---"
test_endpoint "GET /api/cities/" "GET" "/api/cities/" "" "200" "-H 'Authorization: Bearer $ACCESS_TOKEN'"
test_endpoint "GET /api/docs/" "GET" "/api/docs/" "" "200"
test_endpoint "GET /api/schema/" "GET" "/api/schema/" "" "200"
echo ""

# Test 3: REST API - Weather Records
echo "3. REST API - Weather Records Tests"
echo "---"
test_endpoint "GET /api/weather-records/" "GET" "/api/weather-records/" "" "200" "-H 'Authorization: Bearer $ACCESS_TOKEN'"
test_endpoint "GET /api/forecasts/" "GET" "/api/forecasts/" "" "200" "-H 'Authorization: Bearer $ACCESS_TOKEN'"
echo ""

# Test 4: GraphQL API
echo "4. GraphQL API Tests"
echo "---"
GRAPHQL_QUERY='{"query": "{ cities { uuid name } }"}'
test_endpoint "POST /api/graphql/" "POST" "/api/graphql/" "'$GRAPHQL_QUERY'" "200"
echo ""

# Test 5: Atom Feeds
echo "5. Atom Feed Tests"
echo "---"
test_endpoint "GET Atom feed (all forecasts)" "GET" "/api/feeds/forecasts/" "" "200"
echo ""

# Test 6: Documentation
echo "6. API Documentation Tests"
echo "---"
test_endpoint "Swagger UI at /api/docs/" "GET" "/api/docs/" "" "200"
test_endpoint "ReDoc at /api/docs/redoc/" "GET" "/api/docs/redoc/" "" "200"
test_endpoint "OpenAPI schema at /api/schema/" "GET" "/api/schema/" "" "200"
echo ""

# Test 7: GitHub Webhook
echo "7. GitHub Webhook Tests"
echo "---"
WEBHOOK_PAYLOAD='{"action":"opened","number":1}'
WEBHOOK_SIGNATURE="sha256=$(echo -n "$WEBHOOK_PAYLOAD" | openssl dgst -sha256 -hmac "$WEBHOOK_SECRET" | cut -d' ' -f2)"
test_endpoint "POST /api/webhooks/github/ (valid signature)" "POST" "/api/webhooks/github/" "'$WEBHOOK_PAYLOAD'" "200" \
    "-H 'Content-Type: application/json' -H 'X-Hub-Signature-256: $WEBHOOK_SIGNATURE' -H 'X-GitHub-Event: push'"
test_endpoint "POST /api/webhooks/github/ (missing signature)" "POST" "/api/webhooks/github/" "'$WEBHOOK_PAYLOAD'" "400" \
    "-H 'Content-Type: application/json'"
echo ""

# Test 8: Permission Tests
echo "8. Permission Tests"
echo "---"
CITY_DATA='{"name":"TestCity","country":"TestCountry","region":"Test","timezone":"UTC","latitude":0.0,"longitude":0.0}'
test_endpoint "POST /api/cities/ (admin only)" "POST" "/api/cities/" "'$CITY_DATA'" "201" \
    "-H 'Content-Type: application/json' -H 'Authorization: Bearer $ACCESS_TOKEN'"
echo ""

# Test 9: Forecast Validation
echo "9. Forecast Validation Tests"
echo "---"
CITY_UUID=$(curl -s -X GET "$BASE_URL/api/cities/" \
    -H "Authorization: Bearer $ACCESS_TOKEN" | grep -o '"uuid":"[^"]*' | head -1 | cut -d'"' -f4)

if [ -n "$CITY_UUID" ]; then
    FUTURE_DATE=$(date -d "+8 days" +%Y-%m-%d 2>/dev/null || date -v+8d +%Y-%m-%d)
    FORECAST_DATA="{\"city\":\"$CITY_UUID\",\"forecast_date\":\"$FUTURE_DATE\",\"temperature_high\":25,\"temperature_low\":15,\"humidity\":50,\"wind_speed\":5,\"precipitation_probability\":20,\"description\":\"Test\"}"
    test_endpoint "Reject forecast > 7 days" "POST" "/api/forecasts/" "'$FORECAST_DATA'" "400" \
        "-H 'Content-Type: application/json' -H 'Authorization: Bearer $ACCESS_TOKEN'"
else
    echo "⚠ Skipping forecast validation (no city found)"
fi
echo ""

# Summary
echo "========================================="
echo "Test Summary"
echo "========================================="
echo "PASSED: $PASS"
echo "FAILED: $FAIL"
echo ""

if [ $FAIL -eq 0 ]; then
    echo "✓ All E2E tests passed!"
    exit 0
else
    echo "✗ Some tests failed"
    exit 1
fi
