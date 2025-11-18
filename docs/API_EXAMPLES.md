# 📚 API Examples

Complete API documentation is available at: `http://localhost:5000/api-docs`

## Basic Examples

### 1. Register New User

```bash
curl -X POST http://localhost:5000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "name": "John Doe",
    "organization": "Example Inc"
  }'
```

**Response:**
```json
{
  "user_id": "usr_abc123xyz",
  "email": "user@example.com",
  "name": "John Doe",
  "organization": "Example Inc",
  "api_key": "atc_xxxxxxxxxxxxxxxxxxxxx",
  "api_key_id": "key_abc123",
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

### 2. Classify Single Ticket (API Key)

```bash
curl -X POST http://localhost:5000/api/v1/classify \
  -H "Content-Type: application/json" \
  -H "X-API-Key: atc_your_api_key_here" \
  -d '{
    "ticket": "I cannot connect to VPN from my home network"
  }'
```

**Response:**
```json
{
  "category": "Network Issue",
  "confidence": 0.95,
  "priority": "high",
  "provider": "gemini",
  "processing_time": 0.44
}
```

### 3. Classify with JWT Token

```bash
# First, get JWT token
curl -X POST http://localhost:5000/api/v1/auth/jwt/login \
  -H "X-API-Key: atc_your_api_key_here"

# Use JWT token
curl -X POST http://localhost:5000/api/v1/classify \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "ticket": "My password reset is not working"
  }'
```

### 4. Batch Classification

```bash
curl -X POST http://localhost:5000/api/v1/batch \
  -H "Content-Type: application/json" \
  -H "X-API-Key: atc_your_api_key_here" \
  -d '{
    "tickets": [
      "VPN connection keeps dropping",
      "I forgot my password",
      "Need refund for subscription",
      "Can you add dark mode?",
      "Invoice is missing"
    ],
    "webhook_url": "https://example.com/webhook"
  }'
```

**Response:**
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
    {
      "category": "Payment Issue",
      "confidence": 0.95,
      "priority": "high",
      "provider": "gemini"
    },
    {
      "category": "Feature Request",
      "confidence": 0.95,
      "priority": "low",
      "provider": "gemini"
    },
    {
      "category": "Payment Issue",
      "confidence": 0.95,
      "priority": "high",
      "provider": "gemini"
    }
  ]
}
```

### 5. Check API Usage

```bash
curl -X GET http://localhost:5000/api/v1/auth/usage \
  -H "X-API-Key: atc_your_api_key_here"
```

**Response:**
```json
{
  "tier": "free",
  "rate_limits": {
    "hourly_limit": 100,
    "hourly_remaining": 87,
    "daily_limit": 1000,
    "daily_remaining": 987
  },
  "auth_type": "api_key"
}
```

### 6. Create Webhook Subscription

```bash
curl -X POST http://localhost:5000/api/v1/webhooks \
  -H "Content-Type: application/json" \
  -H "X-API-Key: atc_your_api_key_here" \
  -d '{
    "url": "https://your-app.com/webhook",
    "secret": "your-webhook-secret",
    "events": ["classification.completed"]
  }'
```

## Python Examples

```python
import requests

API_BASE = "http://localhost:5000/api/v1"
API_KEY = "atc_your_api_key_here"

# Classify single ticket
response = requests.post(
    f"{API_BASE}/classify",
    headers={"X-API-Key": API_KEY, "Content-Type": "application/json"},
    json={"ticket": "I cannot access my account"}
)

result = response.json()
print(f"Category: {result['category']}")
print(f"Confidence: {result['confidence']}")
print(f"Priority: {result['priority']}")
```

## JavaScript Examples

```javascript
const API_BASE = 'http://localhost:5000/api/v1';
const API_KEY = 'atc_your_api_key_here';

// Classify single ticket
async function classifyTicket(ticketText) {
  const response = await fetch(`${API_BASE}/classify`, {
    method: 'POST',
    headers: {
      'X-API-Key': API_KEY,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ ticket: ticketText })
  });
  
  const result = await response.json();
  return result;
}

// Usage
classifyTicket("VPN not working")
  .then(result => {
    console.log(`Category: ${result.category}`);
    console.log(`Confidence: ${result.confidence}`);
  })
  .catch(error => console.error(error));
```

## Go Examples

```go
package main

import (
    "bytes"
    "encoding/json"
    "fmt"
    "net/http"
)

const APIBase = "http://localhost:5000/api/v1"
const APIKey = "atc_your_api_key_here"

type ClassifyRequest struct {
    Ticket string `json:"ticket"`
}

type ClassifyResponse struct {
    Category       string  `json:"category"`
    Confidence     float64 `json:"confidence"`
    Priority       string  `json:"priority"`
    Provider       string  `json:"provider"`
    ProcessingTime float64 `json:"processing_time"`
}

func classifyTicket(ticketText string) (*ClassifyResponse, error) {
    reqBody := ClassifyRequest{Ticket: ticketText}
    jsonData, _ := json.Marshal(reqBody)
    
    req, _ := http.NewRequest("POST", APIBase+"/classify", bytes.NewBuffer(jsonData))
    req.Header.Set("X-API-Key", APIKey)
    req.Header.Set("Content-Type", "application/json")
    
    client := &http.Client{}
    resp, err := client.Do(req)
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()
    
    var result ClassifyResponse
    json.NewDecoder(resp.Body).Decode(&result)
    
    return &result, nil
}

func main() {
    result, err := classifyTicket("VPN not working")
    if err != nil {
        fmt.Println("Error:", err)
        return
    }
    
    fmt.Printf("Category: %s\n", result.Category)
    fmt.Printf("Confidence: %.2f\n", result.Confidence)
}
```

## Ticket Categories

The system classifies tickets into the following categories:

1. **Network Issue** (Priority: high)
   - Connection problems, VPN, Wi-Fi, network issues

2. **Account Problem** (Priority: high)
   - Account issues, password problems, access issues

3. **Payment Issue** (Priority: high)
   - Payment problems, refunds, invoices

4. **Feature Request** (Priority: low)
   - Requests for new features

5. **Other** (Priority: medium)
   - Everything else

## Error Codes

- `400` - Bad Request (validation error)
- `401` - Unauthorized (invalid API key/JWT)
- `403` - Forbidden
- `429` - Rate limit exceeded
- `500` - Internal server error
- `503` - Service unavailable

## Rate Limits by Tier

| Tier | Requests/Hour | Requests/Day | Batch Size |
|------|---------------|--------------|------------|
| Free | 100 | 1,000 | 10 |
| Starter | 1,000 | 10,000 | 50 |
| Professional | 10,000 | 100,000 | 100 |
| Enterprise | Unlimited | Unlimited | 1,000 |
