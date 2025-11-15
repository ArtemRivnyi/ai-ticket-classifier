# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned
- Swagger/OpenAPI documentation
- CORS middleware configuration
- Input sanitization middleware
- PostgreSQL persistence layer
- Webhook notification system
- Admin dashboard
- Python/JavaScript SDKs

---

## [1.1.0] - 2025-11-15 - GEMINI_API_PROD_READY

### 🎉 Major Features Added

#### Multi-Provider Architecture
- **Added** Google Gemini 2.0 Flash as primary AI provider
- **Added** OpenAI GPT-3.5 as fallback provider
- **Implemented** Circuit Breaker pattern for automatic failover
- **Added** Provider health monitoring and status reporting

#### Authentication & Security
- **Implemented** API Key authentication system
- **Added** Tier-based rate limiting (Free/Starter/Pro/Enterprise)
- **Added** Redis-based session management
- **Implemented** Rate limiting: 100 requests/hour, 1000 requests/day per key
- **Added** Usage tracking and statistics endpoint

#### API Enhancements
- **Added** `/api/v1/batch` endpoint for bulk classification
- **Enhanced** `/api/v1/health` with provider status
- **Added** `/api/v1/auth/register` for API key generation
- **Added** `/api/v1/auth/usage` for usage statistics
- **Implemented** Request/Response logging middleware

#### Monitoring & Observability
- **Added** Prometheus metrics collection
- **Added** Grafana dashboards for visualization
- **Integrated** `/metrics` endpoint for Prometheus scraping
- **Added** Health check with service dependencies
- **Implemented** Custom metrics for classification requests

#### Infrastructure
- **Upgraded** to Python 3.11
- **Added** Docker Compose orchestration
- **Added** Redis container for session management
- **Added** Prometheus container for metrics
- **Added** Grafana container for dashboards
- **Configured** Gunicorn with 4 workers for production
- **Added** Container health checks

### 🔧 Technical Improvements

#### Code Quality
- **Added** Type hints throughout codebase
- **Implemented** Pydantic models for validation
- **Added** Comprehensive error handling
- **Improved** Code organization and structure
- **Added** Logging middleware

#### Performance
- **Optimized** Batch processing endpoint
- **Implemented** Circuit breaker for fast failover
- **Added** Response time tracking
- **Configured** Gunicorn workers for concurrency

#### Testing
- **Added** Test coverage for new endpoints
- **Added** Mock tests for AI providers
- **Enhanced** Error scenario testing
- **Added** Integration tests for batch processing

### 📝 Documentation
- **Rewrote** README.md with comprehensive documentation
- **Added** Architecture diagrams
- **Added** API endpoint documentation
- **Added** Deployment instructions
- **Added** Monitoring setup guide
- **Created** CHANGELOG.md

### 🐛 Bug Fixes
- **Fixed** Empty ticket validation
- **Fixed** Error handling in batch processing
- **Fixed** Rate limit header formatting
- **Fixed** Circuit breaker state management
- **Fixed** Provider initialization errors

### ⚠️ Breaking Changes
- **Changed** API response format to include `provider` field
- **Changed** Health endpoint response structure
- **Removed** Direct OpenAI-only support
- **Migrated** from single provider to multi-provider architecture

### 🔒 Security
- **Added** API key validation
- **Implemented** Rate limiting per key
- **Added** Request sanitization
- **Enhanced** Error messages (no sensitive data leakage)

### 📊 Metrics Added
- `http_requests_total` - Total HTTP requests
- `http_request_duration_seconds` - Request latency histogram
- `classification_requests_total` - Total classification requests
- `classification_duration_seconds` - Classification latency
- `provider_failures_total` - Provider failure counter
- `circuit_breaker_state` - Circuit breaker status gauge
- `batch_classification_size` - Batch size histogram

---

## [1.0.0] - 2024-XX-XX - Initial OpenAI Release

### Added
- Initial Flask RESTful API
- OpenAI GPT-3.5 integration
- `/api/v1/classify` endpoint
- `/api/v1/health` endpoint
- Docker support
- Basic error handling
- Pytest test suite
- CI/CD with GitHub Actions
- Pydantic validation

### Features
- Single ticket classification
- 5 predefined categories
- JSON request/response
- Docker containerization
- Automated testing

---

## Migration Guide: v1.0.0 → v1.1.0

### API Changes

#### 1. Health Endpoint Response
**Before:**
```json
{
  "status": "healthy"
}
```

**After:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-11-15T19:43:52Z",
  "provider_status": {
    "gemini": "available"
  }
}
```

#### 2. Classify Endpoint Response
**Before:**
```json
{
  "category": "Network Issue"
}
```

**After:**
```json
{
  "category": "Network Issue",
  "confidence": 0.95,
  "priority": "high",
  "provider": "gemini",
  "processing_time": 0.54
}
```

#### 3. Authentication Required
All endpoints now require `X-API-Key` header:
```bash
curl -H "X-API-Key: atc_your_key" http://localhost:5000/api/v1/classify
```

### Environment Variables

**New Required Variables:**
```env
GEMINI_API_KEY=your_gemini_key
REDIS_HOST=redis
REDIS_PORT=6379
```

**Deprecated Variables:**
```env
OPENAI_API_KEY  # Now optional (fallback only)
```

### Docker Compose

**Before:** Single container
```yaml
services:
  app:
    build: .
    ports:
      - "5000:5000"
```

**After:** Multi-container setup
```yaml
services:
  app:
    build: .
    ports:
      - "5000:5000"
    depends_on:
      - redis
  
  redis:
    image: redis:7-alpine
  
  prometheus:
    image: prom/prometheus
  
  grafana:
    image: grafana/grafana
```

### Code Migration

If you were using the API in your code:

**Python Before:**
```python
response = requests.post(
    'http://localhost:5000/api/v1/classify',
    json={'ticket': 'Cannot login'}
)
category = response.json()['category']
```

**Python After:**
```python
response = requests.post(
    'http://localhost:5000/api/v1/classify',
    headers={'X-API-Key': 'atc_your_key'},
    json={'ticket': 'Cannot login'}
)
result = response.json()
category = result['category']
confidence = result['confidence']
provider = result['provider']
```

---

## Version History Summary

| Version | Date | Status | Key Features |
|---------|------|--------|--------------|
| 1.1.0 | 2025-11-15 | **Current** | Multi-provider, Auth, Monitoring |
| 1.0.0 | 2024-XX-XX | Deprecated | OpenAI single provider |

---

## Upgrade Instructions

### From v1.0.0 to v1.1.0

1. **Update repository:**
   ```bash
   git checkout GEMINI_API_PROD_READY
   git pull origin GEMINI_API_PROD_READY
   ```

2. **Update `.env` file:**
   ```env
   # Add new required variables
   GEMINI_API_KEY=your_gemini_api_key
   REDIS_HOST=redis
   REDIS_PORT=6379
   
   # Optional: Keep OpenAI as fallback
   OPENAI_API_KEY=your_openai_key
   ```

3. **Rebuild containers:**
   ```bash
   docker-compose down
   docker-compose build --no-cache
   docker-compose up -d
   ```

4. **Generate API key:**
   ```bash
   curl -X POST http://localhost:5000/api/v1/auth/register \
     -H "Content-Type: application/json" \
     -d '{"email": "your@email.com", "tier": "free"}'
   ```

5. **Update your client code** to include API key header

6. **Test the migration:**
   ```bash
   curl -H "X-API-Key: YOUR_KEY" \
     http://localhost:5000/api/v1/health
   ```

---

## Contributors

- **Artem Rivnyi** - Initial work and v1.1.0 production features

---

## Support

For questions about changes or migration issues:
- Open an [Issue](https://github.com/ArtemRivnyi/ai-ticket-classifier/issues)
- Check the [Migration Guide](#migration-guide-v100--v110)
- Review the [README.md](README.md)