# 🚀 Quick Start - Manual Testing

## Fast Testing Guide

### 1. Start Application

```bash
# Activate Python 3.12 environment
venv312\Scripts\activate  # Windows
# or
source venv312/bin/activate  # Linux/Mac

# Start application
python app.py
```

**Wait for:** `🚀 Starting AI Ticket Classifier API on port 5000`

---

### 2. Test Health (Quick Check)

**In browser or curl:**
```
http://localhost:5000/api/v1/health
```

**Expected:** JSON with `"status": "healthy"` and `"gemini": "available"`

---

### 3. Register New User (Get API Key)

**PowerShell:**
```powershell
$response = Invoke-RestMethod -Uri "http://localhost:5000/api/v1/auth/register" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"email":"test@example.com","name":"Test User","organization":"Test Co"}'

# Save API key
$apiKey = $response.api_key
$jwtToken = $response.jwt_token

Write-Host "API Key: $apiKey"
Write-Host "JWT Token: $jwtToken"
```

**curl:**
```bash
curl -X POST http://localhost:5000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","name":"Test User","organization":"Test Co"}'
```

**✅ Copy the `api_key` from response!**

---

### 4. Test Classification (Main Feature)

**Replace `YOUR_API_KEY` with the key from step 3:**

**PowerShell:**
```powershell
$headers = @{
    "Content-Type" = "application/json"
    "X-API-Key" = "YOUR_API_KEY"
}

$body = @{
    ticket = "I cannot connect to VPN"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/v1/classify" `
  -Method Post `
  -Headers $headers `
  -Body $body
```

**curl:**
```bash
curl -X POST http://localhost:5000/api/v1/classify \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{"ticket": "I cannot connect to VPN"}'
```

**Expected response:**
```json
{
  "category": "Network Issue",
  "confidence": 0.95,
  "priority": "high",
  "provider": "gemini",
  "processing_time": 0.44
}
```

**✅ Check:** Category should be one of: Network Issue, Account Problem, Payment Issue, Feature Request, Other

---

### 5. Test Batch Classification

**PowerShell:**
```powershell
$body = @{
    tickets = @(
        "VPN not working",
        "Password reset needed",
        "Refund request"
    )
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/v1/batch" `
  -Method Post `
  -Headers $headers `
  -Body $body
```

**curl:**
```bash
curl -X POST http://localhost:5000/api/v1/batch \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{"tickets": ["VPN not working", "Password reset needed", "Refund request"]}'
```

**✅ Check:** All 3 tickets should be classified successfully

---

### 6. Test Swagger UI

**Open in browser:**
```
http://localhost:5000/api-docs
```

**✅ Check:** Interactive API documentation loads, try "Try it out" feature

---

### 7. Test Error Handling

**Test without API key:**
```bash
curl -X POST http://localhost:5000/api/v1/classify \
  -H "Content-Type: application/json" \
  -d '{"ticket": "Test"}'
```

**Expected:** Status 401 - "API key required"

**Test with invalid key:**
```bash
curl -X POST http://localhost:5000/api/v1/classify \
  -H "Content-Type: application/json" \
  -H "X-API-Key: invalid_key_123" \
  -d '{"ticket": "Test"}'
```

**Expected:** Status 401/403 - "Invalid API key"

---

## ✅ Quick Validation Checklist

After testing, verify:

- [ ] Health endpoint returns healthy
- [ ] User registration works (get API key)
- [ ] Classification works with valid API key
- [ ] Batch classification works
- [ ] Swagger UI loads at /api-docs
- [ ] Error handling works (401 without key)

**If all checked ✅ - API is working correctly!**

---

## Full Testing

For comprehensive testing, see: `MANUAL_TESTING_GUIDE.md`

