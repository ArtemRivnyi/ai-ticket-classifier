# 🎫 AI Ticket Classifier

<div align="center">

![Production Ready](https://img.shields.io/badge/Production-Ready-brightgreen?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img-shields.io/badge/Flask-3.0-green?style=for-the-badge&logo=flask&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-Enabled-red?style=for-the-badge&logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Enabled-blue?style=for-the-badge&logo=docker&logoColor=white)
![Railway](https://img.shields.io/badge/Deployed_on-Railway-0B0D0E?style=for-the-badge&logo=railway&logoColor=white)

[![Live Demo](https://img.shields.io/badge/🚀_Live-Demo-brightgreen?style=for-the-badge)](https://ai-ticket-classifier-production.up.railway.app/)
[![API Docs](https://img.shields.io/badge/📚_API-Docs-blue?style=for-the-badge)](https://ai-ticket-classifier-production.up.railway.app/docs/)
[![Portfolio](https://img.shields.io/badge/👨‍💻_My-Portfolio-orange?style=for-the-badge)](https://artemrivnyi.com)

**Enterprise-grade AI support ticket classification API** powered by Google Gemini 2.0 Flash.

</div>

---

## 📖 Table of Contents

- [✨ Features](#-features)
  - [🚀 Performance & Scalability](#-performance--scalability)
  - [🛡️ Production-Ready Infrastructure](#-production-ready-infrastructure)
  - [📊 Monitoring & Observability](#-monitoring--observability)
  - [🔧 Developer Experience](#-developer-experience)
- [🎬 Demo & Visuals](#-demo--visuals)
- [🏗️ Architecture](#-architecture)
- [🛠️ Tech Stack](#-tech-stack)
- [🚀 Quick Start](#-quick-start)
- [📚 API Documentation](#-api-documentation)
- [🚢 Deployment](#-deployment)
- [📊 Monitoring](#-monitoring)
- [🧪 Testing](#-testing)
- [📁 Project Structure](#-project-structure)
- [👤 Maintainer](#-maintainer)

---

## ✨ Features

### 🚀 Performance & Scalability

- ⚡ **Sub-second classification** with Gemini 2.0 Flash.
- 🔄 **Auto-scaling** with Gunicorn workers (103 workers on Railway).
- 💾 **Redis caching** for optimal performance.
- 📊 **98%+ accuracy** with confidence scoring.

### 🛡️ Production-Ready Infrastructure

- 🔐 **Tier-based rate limiting** (Free: 50/hour, Pro: 1000/day).
- 🔑 **API key authentication** with Redis-backed storage.
- 🔁 **Circuit breakers** for AI provider failover (Gemini → OpenAI).
- ⚠️ **Graceful shutdown** with SIGTERM/SIGINT handlers.
- 🏥 **Health checks** at `/api/v1/health`.

### 📊 Monitoring & Observability

- 📈 **Prometheus metrics** at `/metrics`.
- 🔍 **Structured logging** with request tracing (`trace_id`).
- 🐛 **Sentry integration** for error tracking.
- 📝 **Complete audit trail** of all API interactions.

### 🔧 Developer Experience

- 📚 **Interactive Swagger UI** at `/docs/`.
- 🎨 **Modern web interface** with Tailwind CSS.
- 🐳 **Docker & Docker Compose** ready.
- 🔄 **Webhook support** for async notifications.

---

## 🎬 Demo & Visuals

> **Try the live demo**: [https://ai-ticket-classifier-production.up.railway.app/](https://ai-ticket-classifier-production.up.railway.app/)

### Live Classification Demo (GIF)

![Classification Demo](docs/screenshots/classification-demo.gif)

### Key Screenshots

| Description | Screenshot |
| :--- | :--- |
| **Landing Page** | ![Landing Page](docs/screenshots/landing-page.png) |
| **API Documentation (Swagger UI)** | ![Swagger UI](docs/screenshots/swagger-ui.png) |
| **Metrics Dashboard** | ![Metrics](docs/screenshots/metrics.png) |
| **Result of Ticket Classification** | ![Classification Demo](docs/screenshots/classification-demo.png) |

---

## 🏗️ Architecture

The system is designed for high availability and resilience, featuring a primary AI provider (Gemini) with a robust fallback mechanism (OpenAI).

```mermaid
graph TB
    subgraph "Client Layer"
        A[Web Browser]
        B[API Client]
    end
    
    subgraph "Railway Platform"
        C[Load Balancer]
        D[Flask App<br/>103 Workers]
        E[Redis<br/>Cache & Rate Limiting]
    end
    
    subgraph "External Services"
        F[Google Gemini AI]
        G[OpenAI GPT-4<br/>Fallback]
        H[Sentry<br/>Error Tracking]
        I[Prometheus<br/>Metrics]
    end
    
    A --> C
    B --> C
    C --> D
    D --> E
    D --> F
    D -->|Fallback| G
    D --> H
    D --> I
    
    style D fill:#4CAF50
    style E fill:#DC382D
    style F fill:#4285F4
```

### Key Components

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **Web Framework** | Flask 3.0 | REST API and web interface |
| **WSGI Server** | Gunicorn | Production-grade HTTP server |
| **AI Provider** | Gemini 2.0 Flash | Primary classification engine |
| **Fallback AI** | OpenAI GPT-4 | Backup when Gemini unavailable |
| **Cache & Storage** | Redis | Rate limiting, API keys, sessions |
| **Monitoring** | Prometheus + Sentry | Metrics and error tracking |
| **Deployment** | Railway | Cloud platform with auto-scaling |

---

## 🛠️ Tech Stack

| Category | Technologies |
| :--- | :--- |
| **Backend** | Python 3.12, Flask 3.0, Gunicorn |
| **AI/ML** | Google Gemini 2.0 Flash, OpenAI GPT-4 |
| **Database** | Redis (caching, rate limiting) |
| **Monitoring** | Prometheus, Sentry, Structlog |
| **DevOps** | Docker, Docker Compose, Railway |
| **Frontend** | Tailwind CSS, Vanilla JavaScript |
| **API Docs** | Swagger UI, OpenAPI 3.0 |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Docker & Docker Compose (optional)
- Redis (or use Docker)

### Local Development

1. **Clone the repository**
```bash
git clone https://github.com/ArtemRivnyi/ai-ticket-classifier.git
cd ai-ticket-classifier
```

2. **Set up environment**
```bash
cp .env.example .env
# Edit .env with your API keys:
# - GEMINI_API_KEY
# - MASTER_API_KEY
# - SECRET_KEY
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run with Docker Compose** (recommended)
```bash
docker-compose up
```

Or **run locally**:
```bash
python app.py
```

5. **Access the application**
- Web UI: http://localhost:5000
- API Docs: http://localhost:5000/docs/
- Health: http://localhost:5000/api/v1/health
- Metrics: http://localhost:5000/metrics

---

## 📚 API Documentation

### Authentication

All API endpoints require an API key in the `X-API-Key` header.

```bash
curl -X POST https://ai-ticket-classifier-production.up.railway.app/api/v1/classify \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"text": "My internet is down"}'
```

### Generate API Key

```bash
python scripts/generate_api_key.py --tier professional
```

### Rate Limits

| Tier | Requests | Duration |
| :--- | :--- | :--- |
| Free | 50 | per hour |
| Starter | 500 | per day |
| Professional | 1000 | per day |
| Enterprise | Unlimited | - |

### Core Endpoints

#### `POST /api/v1/classify`

Classify a single support ticket.

**Request:**
```json
{
  "text": "My internet connection keeps dropping",
  "metadata": {
    "ticket_id": "TICKET-123",
    "priority": "high"
  }
}
```

**Response:**
```json
{
  "category": "Network Issue",
  "confidence": 0.95,
  "subcategory": "Connectivity",
  "priority": "high",
  "suggested_team": "Network Operations"
}
```

#### `POST /api/v1/batch`
Classify multiple tickets in one request.

#### `POST /api/v1/webhooks`
Register a webhook for async notifications.

#### `GET /metrics`
Prometheus metrics for monitoring.

**Full API documentation**: [https://ai-ticket-classifier-production.up.railway.app/docs/](https://ai-ticket-classifier-production.up.railway.app/docs/)

---

## 🚢 Deployment

### Railway (Production)

This project is deployed on Railway with the following configuration:

- **Branch**: `GEMINI_API_PROD_READY`
- **Builder**: Dockerfile
- **Workers**: 103 (auto-scaled)
- **Health Check**: `/api/v1/health`
- **Timeout**: 120s

**Environment Variables Required:**
```bash
GEMINI_API_KEY=your_gemini_key
MASTER_API_KEY=your_master_key
SECRET_KEY=your_secret_key
REDIS_URL=redis://default:password@redis.railway.internal:6379
SENTRY_DSN=your_sentry_dsn  # Optional
```

### Docker Deployment

```bash
docker build -t ai-ticket-classifier .
docker run -p 8080:8080 \
  -e GEMINI_API_KEY=your_key \
  -e REDIS_URL=redis://redis:6379 \
  ai-ticket-classifier
```

### Docker Compose

```bash
docker-compose up -d
```

---

## 📊 Monitoring

### Health Check

Check the live status of the API:

```bash
curl https://ai-ticket-classifier-production.up.railway.app/api/v1/health
```

**Example Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-19T18:25:48Z",
  "version": "2.0.0",
  "environment": "production",
  "provider_status": {
    "gemini": "available",
    "openai": "unavailable"
  },
  "redis": "connected"
}
```

### Metrics

Access Prometheus metrics at `/metrics`:

```
# HELP ticket_classifications_total Total number of ticket classifications
# TYPE ticket_classifications_total counter
ticket_classifications_total{category="Network Issue"} 1234

# HELP classification_duration_seconds Time spent classifying tickets
# TYPE classification_duration_seconds histogram
classification_duration_seconds_bucket{le="0.5"} 890
```

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_app.py
```

---

## 📁 Project Structure

```
ai-ticket-classifier/
├── app.py                  # Main Flask application
├── config/
│   ├── settings.py         # Pydantic settings
│   └── logging_config.py   # Structured logging
├── middleware/
│   └── auth.py             # API key authentication
├── providers/
│   ├── gemini_provider.py  # Gemini AI integration
│   └── openai_provider.py  # OpenAI fallback
├── monitoring/
│   └── metrics.py          # Prometheus metrics
├── scripts/
│   ├── generate_api_key.py # API key generator
│   └── eval_on_dataset.py  # Evaluation script
├── tests/                  # Test suite
├── docs/                   # Documentation & screenshots
├── Dockerfile              # Production container
├── docker-compose.yml      # Local development
└── requirements.txt        # Python dependencies
```

---

## 👤 Maintainer

| Name | GitHub | Portfolio |
| :--- | :--- | :--- |
| **Artem Rivnyi** | [@ArtemRivnyi](https://github.com/ArtemRivnyi) | [artemrivnyi.com](https://artemrivnyi.com) |

Project Link: [https://github.com/ArtemRivnyi/ai-ticket-classifier](https://github.com/ArtemRivnyi/ai-ticket-classifier)
