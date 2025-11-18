# 🎫 AI Ticket Classifier API

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://www.docker.com/)
[![Coverage](https://img.shields.io/badge/Coverage-80%25-green.svg)]()
[![Status](https://img.shields.io/badge/Status-Production_Ready_90%25-brightgreen.svg)]()

**Enterprise-grade AI-powered support ticket classification system** built with Flask, Google Gemini AI, Redis, and comprehensive monitoring. Features multi-provider architecture, API key authentication, rate limiting, circuit breakers, and production monitoring with Prometheus & Grafana.

**Status:** ✅ **90% Production Ready** - 357 tests passing (97%), 80% code coverage, Docker-ready deployment.

---

## 📑 Table of Contents

- [✨ Features](#-features)
- [🛠️ Technologies Used](#️-technologies-used)
- [🏗️ Architecture](#️-architecture)
- [🚀 Quick Start](#-quick-start)
- [📡 API Endpoints](#-api-endpoints)
- [🧪 Testing](#-testing)
- [📊 Monitoring](#-monitoring)
- [🔧 Configuration](#-configuration)
- [📈 Production Readiness](#-production-readiness)
- [🐳 Docker Services](#-docker-services)
- [📝 Project Structure](#-project-structure)
- [🔒 Security](#-security)
- [📄 License](#-license)
- [🤝 Contributing](#-contributing)
- [📚 Documentation](#-documentation)
- [🧑‍💻 Contributors](#-contributors)

---

## ✨ Features

### 🎯 Core Capabilities
- **🧠 Multi-Provider AI Classification**: Primary Google Gemini 2.0 Flash with OpenAI fallback support.
- **🔐 API Key Authentication**: Secure access control with tier-based rate limiting.
- **⚡ Batch Processing**: Classify multiple tickets in a single request.
- **🔄 Circuit Breaker Pattern**: Automatic failover and recovery mechanisms.
- **📊 Production Monitoring**: Real-time metrics with Prometheus & Grafana dashboards.
- **💾 Redis Session Management**: Fast, reliable session storage and caching.

### 🔒 Security & Reliability
- **🛡️ Rate Limiting**: Tier-based rate limiting (e.g., 100/month, 1000/day).
- **🔑 Tier-based Access**: Free, Starter, Professional, and Enterprise tiers.
- **🔁 Automatic Restart**: Container health monitoring and self-healing.
- **📝 Request Logging**: Complete audit trail of all API interactions.
- **⚠️ Error Handling**: Comprehensive error responses and fallback strategies.

---

## 🛠️ Technologies Used

- **Python 3.12**
- **Flask 3.0.3**: Web framework
- **Google Gemini 2.0 Flash**: Primary AI provider
- **OpenAI GPT-4.1-mini**: Fallback provider
- **Redis**: Session management and rate limiting
- **Docker & Docker Compose**: Container orchestration
- **Prometheus & Grafana**: Monitoring and observability
- **Gunicorn**: Production WSGI server
- **Pydantic**: Data validation

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Client Application                   │
│              (REST API / SDK / Webhook)                 │
└────────────────────┬────────────────────────────────────┘
                     │ HTTPS (X-API-Key Auth)
                     ▼
┌───────────────────────────────────────────────────────────┐
│                   Flask API Gateway                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Rate Limiter │  │ Auth Middle. │  │   Logging    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────┬──────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Multi-Provider Classifier                  │
│  ┌───────────────────────────────────────────────────┐  │
│  │           Circuit Breaker Manager                 │  │
│  │  ┌──────────────┐         ┌──────────────┐        │  │
│  │  │   Gemini AI  │ Primary │  OpenAI GPT  │Backup  │  │
│  │  └──────────────┘────────▶└──────────────┘       │  │
│  └───────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │
      ┌──────────────┼──────────────┐
      ▼              ▼               ▼
┌──────────┐  ┌──────────┐   ┌──────────┐
│  Redis   │  │Prometheus│   │ Grafana  │
│ DB/Cache │  │ Metrics  │   │Dashboard │
└──────────┘  └──────────┘   └──────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Google Gemini API key

### Docker (Recommended)

1.  **Clone Repository**
    ```bash
    git clone https://github.com/ArtemRivnyi/ai-ticket-classifier.git
    cd ai-ticket-classifier
    ```

2.  **Create `.env` file**
    ```bash
    cp .env.example .env
    ```
    Now, edit the `.env` file and add your `GEMINI_API_KEY`.

3.  **Start Services**
    ```bash
    docker-compose up -d --build
    ```

4.  **Check Health & Docs**
    - **Health Check**: `curl http://localhost:5000/api/v1/health`
    - **API Docs**: [http://localhost:5000/api/v1/docs](http://localhost:5000/api/v1/docs)
    - **Grafana**: [http://localhost:3000](http://localhost:3000) (admin/admin)

---

## 📡 API Endpoints

Base URL: `http://localhost:5000/api/v1`

#### `GET /health`
Checks the operational status of the API and its providers.

#### `POST /classify`
Classifies a single support ticket.
- **Header**: `X-API-Key: your_api_key`
- **Body**: `{"ticket": "I cannot connect to the VPN."}`

#### `POST /classify/batch`
Classifies a list of support tickets.
- **Header**: `X-API-Key: your_api_key`
- **Body**: `{"tickets": ["Ticket 1", "Ticket 2"]}`

---

## 🧪 Testing

```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests with verbose output
python -m pytest tests/ -v

# Run tests with code coverage report
python -m pytest tests/ --cov=. --cov-report=html
```

**Current Test Results:**
- **Total Tests**: 367
- **Passing**: 357 (97%) ✅
- **Skipped**: 10 (due to Python version compatibility)
- **Code Coverage**: 80%

---

## 📊 Monitoring

- **Prometheus Metrics**: `http://localhost:9090`
- **Grafana Dashboards**: `http://localhost:3000` (Credentials: admin/admin)
- **Metrics Endpoint**: `GET /metrics`

---

## 🔧 Configuration

Key environment variables are set in the `.env` file.

- **Required**: `GEMINI_API_KEY`, `SECRET_KEY`
- **Optional**: `OPENAI_API_KEY`, `REDIS_URL`, `FLASK_ENV`, `CORS_ORIGINS`

---

## 📈 Production Readiness

**Status: 90% Production Ready**

### ✅ Completed Features
- [x] Production-grade Flask application with Gunicorn
- [x] API documentation (Swagger/OpenAPI via Flask-RESTX)
- [x] API Key authentication and tier-based rate limiting
- [x] Multi-provider support (Gemini + OpenAI) with circuit breaker
- [x] Docker Compose for one-command deployment
- [x] Monitoring stack (Prometheus & Grafana)
- [x] Comprehensive test coverage (80%, 357 tests passing)
- [x] Input validation with Pydantic models
- [x] Secure CORS and header configuration
- [x] Health checks and metrics endpoints
- [x] Batch processing support
- [x] JWT authentication support
- [x] Redis persistence for sessions and keys
- [x] Container health checks and auto-restart policies

### 💡 Future Enhancements (10% remaining)
- [ ] **SDK Development**: Create client libraries for Python, JavaScript, and Go.
- [ ] **Integration Examples**: Provide guides for Zendesk, Jira, and Slack.
- [ ] **Advanced Monitoring**: Implement specific alerts for provider failures or high latency.
- [ ] **Performance Tuning**: Conduct load testing to optimize for high throughput.
- [ ] **Webhook Improvements**: Use a background task queue (e.g., Celery) for robust delivery.
- [ ] **Increase Test Coverage**: Push core module coverage to >90%.

---

## 🐳 Docker Services

The `docker-compose.yml` includes:
- **app**: The main Flask application.
- **redis**: Redis for rate limiting and caching.
- **prometheus**: Metrics collection.
- **grafana**: Monitoring dashboards.

---

## 📝 Project Structure

```
ai-ticket-classifier/
├── app.py                 # Main Flask application
├── api/                   # API endpoints (Flask-RESTX namespaces)
├── providers/             # AI provider integrations (Gemini, OpenAI)
├── security/              # Auth and rate limiting logic
├── database/              # Database models and configuration
├── tests/                 # Test suite
├── monitoring/            # Prometheus configuration
├── grafana/               # Grafana dashboards
├── docker-compose.yml     # Docker orchestration
└── Dockerfile             # Container definition
```

---

## 🔒 Security

- API key authentication is enforced on all data endpoints.
- Tier-based rate limiting prevents abuse.
- Input is sanitized and validated via Pydantic models.
- CORS is configurable for production environments.
- JWT support is included for user-based authentication schemes.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change. Please make sure to update tests as appropriate.

---

## 📚 Documentation

- **API Documentation**: Interactive docs available at `/api/v1/docs` on the running server.
- **Deployment Guide**: See the [Quick Start](#-quick-start) section.

---

## 🧑‍💻 Contributors

| Contributor | Role | Contact | Links |
| :--- | :--- | :--- | :--- |
| **Artem Rivnyi** | Project Maintainer / Junior Technical Support / DevOps Enthusiast | [artemrivnyi@outlook.com](mailto:artemrivnyi@outlook.com) | [LinkedIn](https://www.linkedin.com/in/artem-rivnyi/) \| [Personal Projects](https://personal-page-devops.onrender.com/) \| [GitHub](https://github.com/ArtemRivnyi) |
