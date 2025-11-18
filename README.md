# 🎫 AI Ticket Classifier API

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://www.docker.com/)
[![Coverage](https://img.shields.io/badge/Coverage-80%25-green.svg)]()
[![Status](https://img.shields.io/badge/Status-Production_Ready_90%25-brightgreen.svg)]()

Enterprise-grade AI-powered support ticket classification system built with Flask, Google Gemini AI, Redis, and comprehensive monitoring. Features multi-provider architecture, API key authentication, rate limiting, circuit breakers, and production monitoring with Prometheus & Grafana.

**Status:** ✅ **90% Production Ready** - 357 tests passing (97%), 80% code coverage, Docker-ready deployment.

## ✨ Features

### Core Capabilities
- **Multi-Provider AI Classification**: Primary Google Gemini 2.0 Flash with OpenAI fallback
- **API Key Authentication**: Secure access control with tier-based rate limiting
- **Batch Processing**: Classify multiple tickets in a single request
- **Circuit Breaker Pattern**: Automatic failover and recovery mechanisms
- **Production Monitoring**: Real-time metrics with Prometheus & Grafana dashboards
- **Redis Session Management**: Fast, reliable session storage and caching

### Security & Reliability
- **Rate Limiting**: Tier-based rate limiting (100-1000 requests/hour)
- **Tier-based Access**: Free, Starter, Professional, and Enterprise tiers
- **Automatic Restart**: Container health monitoring and self-healing
- **Request Logging**: Complete audit trail of all API interactions
- **Error Handling**: Comprehensive error responses and fallback strategies

## 🛠️ Technologies

- **Python 3.12** (required - Python 3.14+ has compatibility issues)
- **Flask 3.0.3**: Web framework
- **Google Gemini 2.0 Flash**: Primary AI provider
- **OpenAI GPT-3.5**: Fallback provider
- **Redis**: Session management and rate limiting
- **Docker & Docker Compose**: Container orchestration
- **Prometheus & Grafana**: Monitoring and observability

## 🚀 Quick Start

### Prerequisites
- **Python 3.12** (required - use `py -3.12` on Windows)
- Docker & Docker Compose
- Google Gemini API key

### Docker (Recommended for Production)

```bash
# Clone repository
git clone <repository-url>
cd ai-ticket-classifier

# Create .env file
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY, SECRET_KEY, JWT_SECRET

# Start all services (app, redis, prometheus, grafana)
docker-compose up -d

# Check health
curl http://localhost:5000/api/v1/health

# View API docs
open http://localhost:5000/api-docs

# View Grafana dashboards
open http://localhost:3000
# Default credentials: admin/admin
```

### Local Development

```bash
# Create virtual environment with Python 3.12
py -3.12 -m venv venv
.\venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GEMINI_API_KEY=your_gemini_api_key
export SECRET_KEY=your_secret_key
export JWT_SECRET=your_jwt_secret

# Run application
python app.py
```

## 📡 API Endpoints

### Health Check
```bash
GET /api/v1/health
```

### Classify Ticket
```bash
POST /api/v1/classify
Content-Type: application/json
X-API-Key: your_api_key

{
  "ticket": "I cannot connect to VPN"
}
```

### Batch Classification
```bash
POST /api/v1/batch
Content-Type: application/json
X-API-Key: your_api_key

{
  "tickets": ["VPN issue", "Password reset", "Refund request"]
}
```

### Register User
```bash
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "name": "John Doe",
  "organization": "Acme Corp"
}
```

### API Documentation
Visit `http://localhost:5000/api-docs` for interactive Swagger documentation.

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html

# View coverage report
open htmlcov/index.html
```

**Current Test Coverage: 80%**

- **Total Tests**: 367
- **Passing**: 357 (97%) ✅
- **Skipped**: 10 (Python 3.14 compatibility)
- **Coverage**: 80% for core modules
- **app.py**: 83% coverage
- **middleware/auth.py**: 67% coverage
- **providers/multi_provider.py**: 62% coverage

## 📊 Monitoring

### Prometheus Metrics
```bash
GET /metrics
```
Access at: http://localhost:9090

### Grafana Dashboards
- Access: http://localhost:3000
- Default credentials: admin/admin
- Pre-configured dashboards for API metrics

### Health Check
```bash
GET /api/v1/health
```

## 🔧 Configuration

### Environment Variables

**Required:**
- `GEMINI_API_KEY` - Google Gemini API key
- `SECRET_KEY` - Flask secret key
- `JWT_SECRET` - JWT token secret (defaults to SECRET_KEY if not set)

**Optional:**
- `OPENAI_API_KEY` - OpenAI API key (for fallback)
- `REDIS_URL` - Redis connection URL (default: redis://redis:6379/0)
- `FLASK_ENV` - Environment: production/development
- `CORS_ORIGINS` - CORS allowed origins (comma-separated)
- `GRAFANA_USER` - Grafana admin user (default: admin)
- `GRAFANA_PASSWORD` - Grafana admin password (default: admin)

## 📈 Production Readiness

**Status: 90% Production Ready**

### ✅ Completed Features
- ✅ Production-grade Flask application
- ✅ API documentation (Swagger/OpenAPI)
- ✅ Rate limiting and authentication
- ✅ Multi-provider support with circuit breaker
- ✅ Docker Compose deployment
- ✅ Monitoring (Prometheus & Grafana)
- ✅ Comprehensive test coverage (80%, 357 tests passing - 97%)
- ✅ Input validation (Pydantic V2)
- ✅ Security best practices
- ✅ Health checks and metrics
- ✅ Batch processing support
- ✅ Webhook notifications
- ✅ JWT authentication
- ✅ Tier-based rate limiting
- ✅ Redis persistence
- ✅ Container health checks
- ✅ Automatic service restart

### 💡 Future Enhancements (10% remaining)
- 💡 SDK development (Python, JavaScript, Go)
- 💡 Integration examples (Zendesk, Jira, Slack)
- 💡 Additional monitoring alerts
- 💡 Load testing and performance optimization
- 💡 Database persistence for API keys (currently Redis-only)
- 💡 Webhook delivery improvements (background tasks with Celery)
- 💡 Increase test coverage to 90%+
- 💡 Additional AI provider integrations (Claude, Anthropic)

## 🐳 Docker Services

The `docker-compose.yml` includes:
- **app**: Main Flask application (Gunicorn with 2 workers)
- **redis**: Redis for rate limiting and caching
- **prometheus**: Metrics collection
- **grafana**: Monitoring dashboards

All services are configured with:
- Health checks
- Automatic restart policies
- Network isolation
- Volume persistence

### Docker Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop all services
docker-compose down

# Rebuild and restart
docker-compose up -d --build

# Check service status
docker-compose ps
```

## 📝 Project Structure

```
ai-ticket-classifier/
├── app.py                 # Main Flask application
├── middleware/            # Authentication and rate limiting
├── providers/             # AI provider integrations
├── api/                   # API endpoints
├── tests/                 # Test suite (367 tests)
├── monitoring/            # Prometheus configuration
├── grafana/              # Grafana dashboards
├── docker-compose.yml     # Docker orchestration
├── Dockerfile             # Container definition
└── requirements.txt      # Python dependencies
```

## 🔒 Security

- API key authentication required for all endpoints
- Tier-based rate limiting
- Input sanitization and validation
- CORS configuration
- Security headers (X-Content-Type-Options, X-Frame-Options, etc.)
- JWT token support
- Redis-based session management

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## 📚 Documentation

- [API Documentation](docs/API.md)
- [Testing Guide](docs/TESTING.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Docker Troubleshooting](docs/DOCKER_TROUBLESHOOTING.md)
- [Testing Commands](TESTING_COMMANDS.md) - Complete guide for testing and monitoring

## 🆘 Support

For issues, questions, or contributions, please open an issue or pull request.

**Version:** 2.0.0  
**Last Updated:** 2025-11-18  
**Python Version:** 3.12 (required)
