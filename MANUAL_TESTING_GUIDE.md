# 🧪 Manual Testing Guide - AI Ticket Classifier

## Complete manual testing instructions for production-ready API

---

## Prerequisites

1. ✅ Python 3.12 environment activated
   ```bash
   venv312\Scripts\activate  # Windows
   # or
   source venv312/bin/activate  # Linux/Mac
   ```

2. ✅ Environment variables configured in `.env`:
   ```env
   GEMINI_API_KEY=your_key_here
   SECRET_KEY=your_secret_key_here
   JWT_SECRET=your_jwt_secret_here
   FLASK_ENV=production
   ```

3. ✅ All dependencies installed:
   ```bash
   pip install -r requirements.txt
   ```

---

## Step 1: Start the Application

### Option A: Development Mode
```bash
python app.py
```

### Option B: Production Mode (Gunicorn)
```bash
gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 120 app:app
```

**Expected output:**
```
🚀 Starting AI Ticket Classifier API on port 5000
Environment: production
✅ Multi-Provider system initialized
✅ Auth middleware loaded
✅ JWT auth loaded
✅ Auth blueprint registered
✅ Metrics initialized
```

**Application will be available at:** `http://localhost:5000`

---

## Step 2: Test Health Endpoint (No Auth Required)

### Using curl:
```bash
curl http://localhost:5000/api/v1/health
```

### Using PowerShell:
```powershell
Invoke-RestMethod -Uri http://localhost:5000/api/v1/health -Method Get
```

### Using browser:
Open: `http://localhost:5000/api/v1/health`

**Expected response:**
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "timestamp": "2025-11-17T18:00:00Z",
  "environment": "production",
  "provider_status": {
    "gemini": "available",
    "openai": "unavailable"
  }
}
```

**✅ Check:** Status should be "healthy", Gemini provider should be "available"

---

## Step 3: Test Swagger UI Documentation

### Open in browser:
```
http://localhost:5000/api-docs
```

**✅ Check:**
- Swagger UI loads without errors
- All endpoints are visible
- Try clicking "Try it out" on any endpoint

---

## Step 4: Register a New User

### Request:
```bash
curl -X POST http://localhost:5000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "name": "Test User",
    "organization": "Test Company"
  }'
```

### Expected response:
```json
{
  "user_id": "usr_xxxxx",
  "email": "test@example.com",
  "name": "Test User",
  "organization": "Test Company",
  "api_key": "atc_xxxxxxxxxxxxxxxxxxxxx",
  "api_key_id": "key_xxxxx",
  "jwt_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "jwt_expires_in": 24,
  "tier": "free",
  "limits": {
    "requests_per_hour": 100,
    "requests_per_day": 1000,
    "batch_size": 10
  },
  "message": "Registration successful! Save your credentials - they will only be shown once."
}
```

**✅ Check:**
- Status code: 201
- `api_key` is present
- `jwt_token` is present
- `tier` is "free"

**⚠️ IMPORTANT:** Save the `api_key` and `jwt_token` - you'll need them for next tests!

---

## Step 5: Test Classification (Single Ticket)

### Using API Key:
```bash
curl -X POST http://localhost:5000/api/v1/classify \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY_HERE" \
  -d '{
    "ticket": "I cannot connect to VPN from my home network"
  }'
```

### Expected response:
```json
{
  "category": "Network Issue",
  "confidence": 0.95,
  "priority": "high",
  "provider": "gemini",
  "processing_time": 0.44
}
```

**✅ Check:**
- Status code: 200
- Category is one of: Network Issue, Account Problem, Payment Issue, Feature Request, Other
- Processing time is reasonable (< 5 seconds)
- Provider is "gemini"

### Test different ticket types:

1. **Network Issue:**
   ```json
   {"ticket": "VPN connection keeps dropping"}
   ```

2. **Account Problem:**
   ```json
   {"ticket": "I forgot my password and cannot reset it"}
   ```

3. **Payment Issue:**
   ```json
   {"ticket": "I was charged twice for my subscription"}
   ```

4. **Feature Request:**
   ```json
   {"ticket": "Can you add dark mode to the application?"}
   ```

---

## Step 6: Test Batch Classification

### Request:
```bash
curl -X POST http://localhost:5000/api/v1/batch \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY_HERE" \
  -d '{
    "tickets": [
      "VPN not working",
      "Password reset needed",
      "Need refund for subscription",
      "Can you add dark mode?",
      "Invoice is missing"
    ]
  }'
```

### Expected response:
```json
{
  "total": 5,
  "successful": 5,
  "failed": 0,
  "processing_time": 1.26,
  "results": [
    {
      "category": "Network Issue",
      "confidence": 0.95,
      "priority": "high",
      "provider": "gemini"
    },
    {
      "category": "Account Problem",
      "confidence": 0.95,
      "priority": "high",
      "provider": "gemini"
    },
    ...
  ]
}
```

**✅ Check:**
- Status code: 200
- All tickets are classified successfully
- Processing time is reasonable
- Results contain valid categories

---

## Step 7: Test JWT Authentication

### Step 7.1: Get JWT Token from API Key
```bash
curl -X POST http://localhost:5000/api/v1/auth/jwt/login \
  -H "X-API-Key: YOUR_API_KEY_HERE"
```

### Expected response:
```json
{
  "jwt_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 24,
  "token_type": "Bearer"
}
```

### Step 7.2: Use JWT Token for Classification
```bash
curl -X POST http://localhost:5000/api/v1/classify \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -d '{
    "ticket": "Cannot access my account"
  }'
```

**✅ Check:**
- Status code: 200
- Classification works with JWT token
- Same response format as API key

---

## Step 8: Test Usage Statistics

### Request:
```bash
curl -X GET http://localhost:5000/api/v1/auth/usage \
  -H "X-API-Key: YOUR_API_KEY_HERE"
```

### Expected response:
```json
{
  "tier": "free",
  "rate_limits": {
    "hourly_limit": 100,
    "hourly_remaining": 95,
    "daily_limit": 1000,
    "daily_remaining": 995
  },
  "auth_type": "api_key"
}
```

**✅ Check:**
- Status code: 200
- Tier is correct
- Rate limits are shown
- Remaining counts decrease after requests

---

## Step 9: Test Error Handling

### Test 1: Missing API Key
```bash
curl -X POST http://localhost:5000/api/v1/classify \
  -H "Content-Type: application/json" \
  -d '{"ticket": "Test ticket"}'
```

**Expected:** Status 401, error message about missing API key

### Test 2: Invalid API Key
```bash
curl -X POST http://localhost:5000/api/v1/classify \
  -H "Content-Type: application/json" \
  -H "X-API-Key: invalid_key_12345" \
  -d '{"ticket": "Test ticket"}'
```

**Expected:** Status 401/403, error message about invalid API key

### Test 3: Empty Ticket
```bash
curl -X POST http://localhost:5000/api/v1/classify \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY_HERE" \
  -d '{"ticket": ""}'
```

**Expected:** Status 400, validation error

### Test 4: Missing Ticket Field
```bash
curl -X POST http://localhost:5000/api/v1/classify \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY_HERE" \
  -d '{}'
```

**Expected:** Status 400, validation error

### Test 5: Rate Limit Exceeded (if possible)
Make 101 requests in quick succession to test rate limiting.

**Expected:** Status 429 after rate limit is exceeded

---

## Step 10: Test Prometheus Metrics

### Request:
```bash
curl http://localhost:5000/metrics
```

**✅ Check:**
- Status code: 200
- Response contains Prometheus format metrics
- Metrics include: `api_requests_total`, `api_request_duration_seconds`, `classifications_total`

---

## Step 11: Test Webhook Endpoint

### Request:
```bash
curl -X POST http://localhost:5000/api/v1/webhooks \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY_HERE" \
  -d '{
    "url": "https://example.com/webhook",
    "secret": "webhook_secret_123",
    "events": ["classification.completed"]
  }'
```

**Expected:** Status 201, webhook created response

---

## Step 12: Test API Key Management

### List API Keys:
```bash
curl -X GET http://localhost:5000/api/v1/auth/keys \
  -H "X-API-Key: YOUR_API_KEY_HERE"
```

### Create New API Key:
```bash
curl -X POST http://localhost:5000/api/v1/auth/keys \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY_HERE" \
  -d '{
    "name": "My Second API Key"
  }'
```

**✅ Check:**
- New API key is created
- Can use new key for requests

---

## Step 13: Test CORS (if testing from browser)

### Using JavaScript fetch:
```javascript
fetch('http://localhost:5000/api/v1/health', {
  method: 'GET',
  headers: {
    'Origin': 'http://localhost:3000'
  }
})
.then(response => response.json())
.then(data => console.log(data));
```

**✅ Check:** CORS headers are present in response

---

## Test Results Checklist

After completing all tests, verify:

- [ ] Health endpoint returns healthy status
- [ ] Swagger UI loads and is accessible
- [ ] User registration works and returns API key + JWT
- [ ] Single classification works with API key
- [ ] Single classification works with JWT token
- [ ] Batch classification works correctly
- [ ] Usage statistics endpoint works
- [ ] Error handling works (401, 400, 429)
- [ ] Prometheus metrics endpoint returns data
- [ ] Webhook creation works
- [ ] API key management works
- [ ] CORS is configured (if testing from browser)
- [ ] Rate limiting works (if tested)
- [ ] All categories are classified correctly
- [ ] Processing times are reasonable

---

## Performance Benchmarks

Expected performance:
- **Single classification:** < 1 second
- **Batch (10 tickets):** < 3 seconds
- **Batch (100 tickets):** < 30 seconds
- **Health check:** < 50ms

---

## Troubleshooting

### Application won't start:
- Check GEMINI_API_KEY is set in .env
- Check Python 3.12 is activated
- Check all dependencies are installed

### Classification fails:
- Check GEMINI_API_KEY is valid
- Check internet connection
- Check logs for detailed error messages

### API key authentication fails:
- Verify API key format: `atc_xxxxx`
- Check API key is saved correctly
- Verify headers are sent correctly: `X-API-Key: your_key`

### Rate limit errors:
- Normal for free tier (100/hour)
- Wait or use higher tier for testing

---

## Quick Test Script

Save this as `quick_test.sh` (Linux/Mac) or `quick_test.bat` (Windows):

```bash
#!/bin/bash
# Quick test script

API_KEY="your_api_key_here"
BASE_URL="http://localhost:5000"

echo "Testing Health..."
curl -s "$BASE_URL/api/v1/health" | jq

echo -e "\nTesting Classification..."
curl -s -X POST "$BASE_URL/api/v1/classify" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"ticket": "VPN not working"}' | jq

echo -e "\nTesting Batch..."
curl -s -X POST "$BASE_URL/api/v1/batch" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"tickets": ["VPN not working", "Password reset"]}' | jq
```

---

## Summary

After completing all manual tests:
- ✅ All endpoints are working
- ✅ Authentication works (API key + JWT)
- ✅ Classification is accurate
- ✅ Error handling is proper
- ✅ Monitoring is enabled

**Your application is production-ready!** 🚀

