# 🎫 AI Ticket Classifier - Production Ready

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://www.docker.com/)
[![Gemini](https://img.shields.io/badge/Google-Gemini_2.0_Flash-orange.svg)](https://deepmind.google/technologies/gemini/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Production](https://img.shields.io/badge/Status-Production_Ready_90%25-brightgreen.svg)]()
[![Coverage](https://img.shields.io/badge/Coverage-80%25-green.svg)]()

**Enterprise-grade AI-powered support ticket classification system** built with Flask, Google Gemini AI, Redis, and comprehensive monitoring. Features multi-provider architecture, API key authentication, rate limiting, circuit breakers, and production monitoring with Prometheus & Grafana.

**Status:** ✅ **Production Ready (90%)** - See [PRODUCTION_READINESS_REPORT.md](PRODUCTION_READINESS_REPORT.md) for details.

---

## 📑 Table of Contents

- [✨ Features](#-features)
- [🛠️ Technologies Used](#️-technologies-used)
- [🏗️ Architecture](#️-architecture)
- [🚀 Quick Start](#-quick-start)
- [🔑 API Authentication](#-api-authentication)
- [📡 API Endpoints](#-api-endpoints)
- [🧪 Testing](#-testing)
- [📊 Monitoring](#-monitoring)
- [🔧 Development](#-development)
- [📈 Production Status](#-production-status)
- [📄 License](#-license)

---

## ✨ Features

### 🎯 Core Capabilities
- **🧠 Multi-Provider AI Classification**: Primary Google Gemini 2.0 Flash integration with OpenAI fallback support
- **🔐 API Key Authentication**: Secure access control with tier-based rate limiting
- **⚡ Batch Processing**: Classify multiple tickets in a single request
- **🔄 Circuit Breaker Pattern**: Automatic failover and recovery mechanisms
- **📊 Production Monitoring**: Real-time metrics with Prometheus & Grafana dashboards
- **💾 Redis Session Management**: Fast, reliable session storage and caching

### 🔒 Security & Reliability
- **🛡️ Rate Limiting**: Tier-based rate limiting (100-1000 requests/hour)
- **🔑 Tier-based Access**: Free, Starter, Professional, and Enterprise tiers
- **🔁 Automatic Restart**: Container health monitoring and self-healing
- **📝 Request Logging**: Complete audit trail of all API interactions
- **⚠️ Error Handling**: Comprehensive error responses and fallback strategies

### 🚀 DevOps Ready
- **🐳 Docker Compose**: Complete orchestration for app, Redis, Prometheus, Grafana
- **✅ Health Checks**: Built-in endpoint for service monitoring
- **📈 Metrics Export**: Prometheus-compatible metrics endpoint
- **🔧 Environment Config**: 12-factor app configuration management
- **🧪 Test Coverage**: Comprehensive pytest test suite (80% coverage)

---

## 🛠️ Technologies Used

### Backend Stack
- **Python 3.12**: Required version
- **Flask 3.0**: Lightweight web framework
- **Gunicorn**: Production WSGI server (4 workers)
- **Pydantic V2**: Request/response validation
- **Redis**: Session management and caching

### AI/ML
- **Google Gemini 2.0 Flash**: Primary classification provider
- **OpenAI GPT-3.5**: Fallback provider (optional)
- **Circuit Breaker Pattern**: Provider failover logic

### Infrastructure
- **Docker & Docker Compose**: Container orchestration
- **Prometheus**: Metrics collection and alerting
- **Grafana**: Monitoring dashboards
- **GitHub Actions**: CI/CD pipeline (ready)

### Development Tools
- **Pytest**: Testing framework
- **Pytest-mock**: Mocking for tests
- **Pytest-cov**: Coverage reporting

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.12** (required)
- Docker & Docker Compose (for production)
- Redis (optional, in-memory fallback available)
- Google Gemini API key

**⚠️ Note:** This project requires Python 3.12. Python 3.14+ has known compatibility issues with `google-generativeai`.

### Local Development

```bash
# Clone repository
git clone <repository-url>
cd ai-ticket-classifier

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GEMINI_API_KEY=your_gemini_api_key
export MASTER_API_KEY=your_master_api_key
export FLASK_ENV=development

# Run application
python app.py
```

### Docker Production

```bash
# Start all services (recommended - without PostgreSQL)
docker-compose -f docker-compose.simple.prod.yml up -d

# Or with PostgreSQL (if needed)
docker-compose -f docker-compose.prod.yml up -d

# Check health
curl http://localhost:5000/api/v1/health

# View API docs
open http://localhost:5000/api-docs
```

**Note:** PostgreSQL is optional. Use `docker-compose.simple.prod.yml` for faster startup.

---

## 🔑 API Authentication

All endpoints (except `/health`) require API key authentication:

```bash
curl -H "X-API-Key: your_api_key" http://localhost:5000/api/v1/classify
```

### Register New User

```bash
curl -X POST http://localhost:5000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "name": "John Doe",
    "organization": "Acme Corp"
  }'
```

---

## 📡 API Endpoints

### Health Check
```
GET /api/v1/health
```

### Classify Ticket
```
POST /api/v1/classify
Content-Type: application/json
X-API-Key: your_api_key

{
  "ticket": "I cannot connect to VPN"
}
```

### Batch Classification
```
POST /api/v1/batch
Content-Type: application/json
X-API-Key: your_api_key

{
  "tickets": ["VPN issue", "Password reset", "Refund request"]
}
```

### API Documentation
Visit `/api-docs` when server is running for interactive Swagger documentation.

For complete API reference, see [docs/API.md](docs/API.md).

---

## 🧪 Testing

### Run All Tests
```bash
python run_all_tests.py
```

### Run with Coverage
```bash
pytest tests/ --cov=app --cov=middleware --cov=providers --cov=api --cov=security --cov-report=html
```

**Current Coverage: 80%**

For detailed testing guide, see [docs/TESTING.md](docs/TESTING.md).

---

## 📊 Monitoring

### Prometheus Metrics
```
GET /metrics
```

### Grafana Dashboards
- Access: http://localhost:3000
- Default credentials: admin/admin

### Health Check
```
GET /api/v1/health
```

For deployment details, see [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

---

## 🔧 Development

### Project Structure
See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for detailed structure.

### Environment Variables
- `GEMINI_API_KEY` - Required: Google Gemini API key
- `OPENAI_API_KEY` - Optional: OpenAI API key (for fallback)
- `MASTER_API_KEY` - Required: Master API key for admin access
- `REDIS_URL` - Optional: Redis connection URL (default: redis://redis:6379)
- `DATABASE_URL` - Optional: PostgreSQL connection URL
- `FLASK_ENV` - Environment: production/development
- `JWT_SECRET` - JWT token secret key
- `CORS_ORIGINS` - CORS allowed origins (comma-separated)

---

## 📈 Production Status

**Readiness: 90%**

### ✅ Completed Features
- ✅ Production-grade Flask application
- ✅ API documentation (Swagger/OpenAPI)
- ✅ Rate limiting and authentication
- ✅ Multi-provider support with circuit breaker
- ✅ Docker Compose deployment
- ✅ Monitoring (Prometheus & Grafana)
- ✅ Comprehensive test coverage (80%)
- ✅ Input validation (Pydantic V2)
- ✅ Security best practices

### 💡 Optional Enhancements
- 💡 SDK development (Python, JavaScript, Go)
- 💡 Integration examples (Zendesk, Jira, Slack)
- 💡 Additional monitoring alerts

For detailed production readiness report, see [PRODUCTION_READINESS_REPORT.md](PRODUCTION_READINESS_REPORT.md).

---

## 💰 Commercialization Model

**API-as-a-Service:**

| Tier | Price | Requests/Month | Batch Size |
|------|-------|----------------|------------|
| **Free** | $0 | 100 | 10 |
| **Starter** | $49 | 1,000 | 50 |
| **Professional** | $199 | 10,000 | 100 |
| **Enterprise** | $0.01/request | Unlimited | 1,000 |

**B2B Integration:** Revenue share 20-30%

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🧰 Maintainer

For issues, questions, or contributions, please open an issue or pull request.

**Version:** 2.0.0  
**Last Updated:** 2025-01-17
