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

The GIF is now clearly visible and not hidden in a collapsible section.

![Classification Demo](https://private-us-east-1.manuscdn.com/sessionFile/lbgvHXmokFHrcPfQPhB8Mk/sandbox/zmvpAqn2UjiYyeyNEh2deF-images_1763584602613_na1fn_L2hvbWUvdWJ1bnR1L2FpLXRpY2tldC1jbGFzc2lmaWVyL2RvY3Mvc2NyZWVuc2hvdHMvY2xhc3NpZmljYXRpb24tZGVtbw.gif?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9wcml2YXRlLXVzLWVhc3QtMS5tYW51c2Nkbi5jb20vc2Vzc2lvbkZpbGUvbGJndkhYbW9rRkhyY1BmUVBoQjhNay9zYW5kYm94L3ptdnBBcW4yVWppWXlleU5FaDJkZUYtaW1hZ2VzXzE3NjM1ODQ2MDI2MTNfbmExZm5fTDJodmJXVXZkV0oxYm5SMUwyRnBMWFJwWTJ0bGRDMWpiR0Z6YzJsbWFXVnlMMlJ2WTNNdmMyTnlaV1Z1YzJodmRITXZZMnhoYzNOcFptbGpZWFJwYjI0dFpHVnRidy5naWYiLCJDb25kaXRpb24iOnsiRGF0ZUxlc3NUaGFuIjp7IkFXUzpFcG9jaFRpbWUiOjE3OTg3NjE2MDB9fX1dfQ__&Key-Pair-Id=K2HSFNDJXOU9YS&Signature=Ikg57t5esBPrkzY~ZG17sC1w-1UQMGGE3iUf8jn3NvwDmcYtqTr9O3SDcoIKGqv~s1nKoTQiTJ3p24o1BYCY8a6Gera79FUmArAcCMUIep~W5R~YPOXy-hwKMNVmUfG0WJSZuJ7oymTsDnSST77BUBhzGkpYQL4ozNDfrlAX958d4eQUtzKfiPs9v-2rsSSii5XcKuVcCCte4elQo5jTaGYKDKIH7FTLQZyeDyh1fWCqtrDdtT2KXTGPSLkqvmxkX178BCb2cpGxzIo2mSY-Uvm5EMOpbq7M-eR7P6ASiGr35mJlEnqNrnSZgLn7ViHZsV7mGWYcVHhc-u6lvPRK5w__)

### Key Screenshots

| Description | Screenshot |
| :--- | :--- |
| **Landing Page** | ![Landing Page](https://private-us-east-1.manuscdn.com/sessionFile/lbgvHXmokFHrcPfQPhB8Mk/sandbox/zmvpAqn2UjiYyeyNEh2deF-images_1763584602615_na1fn_L2hvbWUvdWJ1bnR1L2FpLXRpY2tldC1jbGFzc2lmaWVyL2RvY3Mvc2NyZWVuc2hvdHMvbGFuZGluZy1wYWdl.png?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9wcml2YXRlLXVzLWVhc3QtMS5tYW51c2Nkbi5jb20vc2Vzc2lvbkZpbGUvbGJndkhYbW9rRkhyY1BmUVBoQjhNay9zYW5kYm94L3ptdnBBcW4yVWppWXlleU5FaDJkZUYtaW1hZ2VzXzE3NjM1ODQ2MDI2MTVfbmExZm5fTDJodmJXVXZkV0oxYm5SMUwyRnBMWFJwWTJ0bGRDMWpiR0Z6YzJsbWFXVnlMMlJ2WTNNdmMyTnlaV1Z1YzJodmRITXZiR0Z1WkdsdVp5MXdZV2RsLnBuZyIsIkNvbmRpdGlvbiI6eyJEYXRlTGVzc1RoYW4iOnsiQVdTOkVwb2NoVGltZSI6MTc5ODc2MTYwMH19fV19&Key-Pair-Id=K2HSFNDJXOU9YS&Signature=Fx578J-QO8PdXPc-8ONv4ZSwoF74XB4qQNg~2h9~a1FouoVga~VJmpp8Cp3i7ThfHnDq7-Svez19r0MUYtx8AhO3QlQD2WW7ZuDAk2Hmy5plQgwVx~3NAOqIptrmljH39pe6zTL1Wh-Na0E9MKb2rlC5cBl8sXyztks4f4O0FLEKWQV~JUe5PzSYquxkYrWcLj2EbfwcMOKo5GXaLKH-6gMZGLg3IRSfkNS3-nY9SDyzrf8eR5-zjsHpeHvWRfv9m4KX1JyBM3xx6PWItlj0PgLI52locL1kDLlMEfOk3c-F04q7cMZvcQmNJ-r~n89OTXlYcwRyYJA~E9lQ9sivrg__) |
| **API Documentation (Swagger UI)** | ![Swagger UI](https://private-us-east-1.manuscdn.com/sessionFile/lbgvHXmokFHrcPfQPhB8Mk/sandbox/zmvpAqn2UjiYyeyNEh2deF-images_1763584602617_na1fn_L2hvbWUvdWJ1bnR1L2FpLXRpY2tldC1jbGFzc2lmaWVyL2RvY3Mvc2NyZWVuc2hvdHMvc3dhZ2dlci11aQ.png?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9wcml2YXRlLXVzLWVhc3QtMS5tYW51c2Nkbi5jb20vc2Vzc2lvbkZpbGUvbGJndkhYbW9rRkhyY1BmUVBoQjhNay9zYW5kYm94L3ptdnBBcW4yVWppWXlleU5FaDJkZUYtaW1hZ2VzXzE3NjM1ODQ2MDI2MTdfbmExZm5fTDJodmJXVXZkV0oxYm5SMUwyRnBMWFJwWTJ0bGRDMWpiR0Z6YzJsbWFXVnlMMlJ2WTNNdmMyTnlaV1Z1YzJodmRITXZjM2RoWjJkbGNpMTFhUS5wbmciLCJDb25kaXRpb24iOnsiRGF0ZUxlc3NUaGFuIjp7IkFXUzpFcG9jaFRpbWUiOjE3OTg3NjE2MDB9fX1dfQ__&Key-Pair-Id=K2HSFNDJXOU9YS&Signature=a6vv0x6hAW9f5HdetHFNPcQUOds9sHoa68vmwqkHX9aPVcHTnRRO8ed-0xJ4FJRifX3hlHPMba-i24BDNXonYbjACe~r0mEpFd1lka1VHm1giHXt5U7Xr4AA2WccJrMSgA8z-YyintrIVtpqCusQD31r3qgRvgX7hXvL5M8s9VF1wFMkBid2lqjtmyAM3fvN6x0vV9fKsumd9bGPbTGNIJcIGU~Ov7FKk-mpZLw4JJR~vJwI~bJu-AMZ8AvN--MR5JVXxP1Zn~xff~vUEsCsqNDtNR7kRnH5Jq4KgRvRgrq8PFEiolHAYIxZnzHuL70GBlL79SyEAnTnheF6tR0cGQ__) |
| **Metrics Dashboard** | ![Metrics](https://private-us-east-1.manuscdn.com/sessionFile/lbgvHXmokFHrcPfQPhB8Mk/sandbox/zmvpAqn2UjiYyeyNEh2deF-images_1763584602618_na1fn_L2hvbWUvdWJ1bnR1L2FpLXRpY2tldC1jbGFzc2lmaWVyL2RvY3Mvc2NyZWVuc2hvdHMvbWV0cmljcw.png?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9wcml2YXRlLXVzLWVhc3QtMS5tYW51c2Nkbi5jb20vc2Vzc2lvbkZpbGUvbGJndkhYbW9rRkhyY1BmUVBoQjhNay9zYW5kYm94L3ptdnBBcW4yVWppWXlleU5FaDJkZUYtaW1hZ2VzXzE3NjM1ODQ2MDI2MThfbmExZm5fTDJodmJXVXZkV0oxYm5SMUwyRnBMWFJwWTJ0bGRDMWpiR0Z6YzJsbWFXVnlMMlJ2WTNNdmMyTnlaV1Z1YzJodmRITXZiV1YwY21samN3LnBuZyIsIkNvbmRpdGlvbiI6eyJEYXRlTGVzc1RoYW4iOnsiQVdTOkVwb2NoVGltZSI6MTc5ODc2MTYwMH19fV19&Key-Pair-Id=K2HSFNDJXOU9YS&Signature=bYrXsQisu6-uKDTHM21yBTw~JnGjIGK1mvRygxFS0~BlaZpfMEnP6P4u1PNSOsY6r5INacTo8aIoQDkEBHWO~eSKgnDAOFQkBcONMc4qRsVkeBWbXEQ-Mc4i5oGz74I8kJTxYq0YhpFd1YmnbieyjrpWrZZQu9QNqckEuDNY9fWqZBvt73yna2bhDTD0wu-jx7-TXJI1M7NVTOKIJVCOs7yCZmGiYB8Dp2ul4hjczPmBWxEb2WLv4XgE6qoz3Ut-s2aPldV~fHmo0Kj0PQtknQ~ylHc18pnJQbVfjTGk63mRt0PS~35yLu2IA7AWGtgArFJAmKV28iQ1gy~u1PNxdg__) |
| **Result of Ticket Classification** | ![Classification Demo](https://private-us-east-1.manuscdn.com/sessionFile/lbgvHXmokFHrcPfQPhB8Mk/sandbox/zmvpAqn2UjiYyeyNEh2deF-images_1763584602619_na1fn_L2hvbWUvdWJ1bnR1L2FpLXRpY2tldC1jbGFzc2lmaWVyL2RvY3Mvc2NyZWVuc2hvdHMvY2xhc3NpZmljYXRpb24tZGVtbw.png?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9wcml2YXRlLXVzLWVhc3QtMS5tYW51c2Nkbi5jb20vc2Vzc2lvbkZpbGUvbGJndkhYbW9rRkhyY1BmUVBoQjhNay9zYW5kYm94L3ptdnBBcW4yVWppWXlleU5FaDJkZUYtaW1hZ2VzXzE3NjM1ODQ2MDI2MTlfbmExZm5fTDJodmJXVXZkV0oxYm5SMUwyRnBMWFJwWTJ0bGRDMWpiR0Z6YzJsbWFXVnlMMlJ2WTNNdmMyTnlaV1Z1YzJodmRITXZZMnhoYzNOcFptbGpZWFJwYjI0dFpHVnRidy5wbmciLCJDb25kaXRpb24iOnsiRGF0ZUxlc3NUaGFuIjp7IkFXUzpFcG9jaFRpbWUiOjE3OTg3NjE2MDB9fX1dfQ__&Key-Pair-Id=K2HSFNDJXOU9YS&Signature=JZGIqayvrr7n1SSXs9HZai5Zz8-a6E2eTnmigFsVE~b9GG1n2WjSMBLBCsM78Q70Z9RVUieMxlmvmtub0BmP5sWUcWYXfIeGuDn0hkGaXi5kXquQXvEJxS8JhCIWlRXdgTVTrVnYVVEWgA8VH94JeKZb2v3VlNBrkzHlvQ2Qe3TCekOUyRr68pgNDGB3EY7-qFwO0K9hamY0lwblwlHtEe9h5N1Ho4mSknhDbPyB1iOdnq9gd9U8Ra2dQSXTEHHGYWite7y~XEhjN0qvRpfBY2H2VyS08DVqnWElnTN2R6DUNKyy-dM1zJdcZfCE8tBaSgLBQvl-UOdvVtkk3x2jOQ__) |

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
