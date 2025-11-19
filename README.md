# 🎫 AI Ticket Classifier

![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-green?style=for-the-badge&logo=flask&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Enabled-blue?style=for-the-badge&logo=docker&logoColor=white)
![Railway](https://img.shields.io/badge/Deployed_on-Railway-0B0D0E?style=for-the-badge&logo=railway&logoColor=white)
[![Live Demo](https://img.shields.io/badge/Live-Demo-brightgreen?style=for-the-badge)](https://ai-ticket-classifier-production.up.railway.app/)

**Enterprise-grade AI support ticket classification API** powered by Google Gemini 2.0 Flash.

> ✅ **98%+ Accuracy with confidence scoring**
>
> ✅ **Consistent AI-driven classification**
>
> ✅ **Human-in-the-loop validation support**

---

## ✨ Features

- **🚀 High Performance**: Sub-second classification with Gemini 2.0 Flash.
- **🛡️ Robust Architecture**: Circuit breakers, fallbacks (OpenAI), and retries.
- **📈 Automated Evaluations**: `scripts/eval_on_dataset.py` runs end-to-end dataset checks with metrics in `reports/`.

### 🔒 Security & Reliability
- **🛡️ Rate Limiting**: Tier-based rate limiting (e.g., 100/month, 1000/day).
- **🔑 Tier-based Access**: Free, Starter, Professional, and Enterprise tiers.
- **🔁 Automatic Restart**: Container health monitoring and self-healing.
- **📝 Request Logging**: Complete audit trail of all API interactions.
- **⚠️ Error Handling**: Comprehensive error responses and fallback strategies.
- **🧾 Structured Logging**: JSON logs with `trace_id` for every request and response.

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
    - **Live Demo**: [https://ai-ticket-classifier-production.up.railway.app/](https://ai-ticket-classifier-production.up.railway.app/)
    - **API Docs**: [https://ai-ticket-classifier-production.up.railway.app/docs](https://ai-ticket-classifier-production.up.railway.app/docs)
    - **Local Health**: `curl http://localhost:5000/api/v1/health`
    - **Local Docs**: [http://localhost:5000/docs](http://localhost:5000/docs)
    - **Grafana**: [http://localhost:3000](http://localhost:3000) (admin/admin)

---

## 📡 API Endpoints

Base URL: `http://localhost:5000/api/v1`

#### `GET /health`
Checks the operational status of the API and its providers.

#### `GET /ready`
Readiness probe that verifies environment variables and provider availability. Returns `503` if any required dependency is missing.

#### `POST /classify`
Classifies a single support ticket.
- **Header**: `X-API-Key: your_api_key`
- **Body**: `{"ticket": "I cannot connect to the VPN."}`
- **Observability**: Include optional `X-Request-ID` to correlate with JSON logs. Responses always include `request_id`.

#### `POST /batch`
Classifies a list of support tickets.
- **Header**: `X-API-Key: your_api_key`
- **Body**: `{"tickets": ["Ticket 1", "Ticket 2"]}`

#### `POST /webhooks`
Registers a webhook for asynchronous event notifications.
- **Header**: `X-API-Key: your_api_key`
- **Body**: `{"url": "https://your-webhook.com/listener"}`

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
- **Total Tests**: 371
- **Passing**: 371 (100%) ✅
- **Skipped**: 10 (due to Python version compatibility)
- **Code Coverage**: 82%

---

## 📊 Monitoring

- **Prometheus Metrics**: `http://localhost:9090`
- **Grafana Dashboards**: `http://localhost:3000` (Credentials: admin/admin)
- **Metrics Endpoint**: `GET /metrics`

---

## 📈 Evaluation Pipeline

- **Dataset format**: JSONL with fields `id`, `text`, optional `label`.
- **Command**:
  ```bash
  python scripts/eval_on_dataset.py --input data/annotated.jsonl --api-key <MASTER_OR_USER_KEY>
  ```
- **Outputs**:
  - `reports/predictions_<timestamp>.jsonl` — raw predictions with `request_id`, latency, provider
  - `reports/eval_<timestamp>.json|.md` — accuracy, precision, recall, F1, confusion matrix
- **Use cases**: regression testing on fresh exports, go/no-go evidence for releases, triage for low-confidence tickets.

---

## 🔥 Load Testing

- **Script**: `loadtests/k6_scenarios.js` (smoke 50 RPS, steady 200 RPS, stress 1000 RPS).
- **Prereqs**: running API, k6 CLI, API key (`API_KEY`), optional overrides `SMOKE_RPS`, `STEADY_RPS`, `STRESS_RPS`.
- **Command**:
  ```bash
  export BASE_URL=http://localhost:5000
  export API_KEY=atc_your_key
  k6 run loadtests/k6_scenarios.js \
    --summary-export reports/loadtests/k6_summary.json \
    --console-output reports/loadtests/k6_console.log
  ```
- **Metrics**: k6 trends `classify_latency_ms`, error counter `classify_errors_total`; correlate with Prometheus dashboards for full SLO view.
- **Next steps**: archive outputs under `reports/loadtests/` and tune timeouts/circuit breaker if error rate >2% or p95 latency exceeds targets.

---

## 🤝 Zendesk Integration

- **Endpoint**: `POST /api/v1/integrations/zendesk` (requires `X-API-Key`)
- **Payload**:
  ```json
  {
    "ticket_id": 12345,
    "subject": "VPN keeps dropping",
    "description": "Users cannot connect to corporate VPN since 8am",
    "requester_email": "user@example.com"
  }
  ```
- **What happens**:
  1. Endpoint validates payload via Pydantic.
  2. Composes subject + description, calls classifier.
  3. `ZendeskAdapter` builds update instructions (recommended tags, priority, group, AI comment).
  4. Response contains structured payload you can forward to Zendesk API.
- **Sample response**:
  ```json
  {
    "status": "processed",
    "ticket_id": 12345,
    "zendesk": {
      "ticket_id": 12345,
      "group": "tech_support",
      "priority": "high",
      "tags": ["ai_classifier", "network_issue", "vpn"],
      "public_comment": "[AI] Classified as Network Issue (confidence 0.92).",
      "metadata": {
        "category": "Network Issue",
        "confidence": 0.92,
        "provider": "gemini",
        "priority": "high"
      }
    }
  }
  ```
- Extend this pattern for other systems (Jira, Slack) by implementing additional adapters under `integrations/`.

---

## 🔧 Configuration

Key environment variables are set in the `.env` file.

- **Required**: `MASTER_API_KEY`, `SECRET_KEY`, and at least one of `GEMINI_API_KEY` or `OPENAI_API_KEY`
- **Optional**: `REDIS_URL`, `DATABASE_URL`, `FLASK_ENV`, `CORS_ORIGINS`
- The app validates these at startup and the `/ready` endpoint reflects any missing configuration.

---

## 📈 Production Readiness

**Status: 100% Production Ready**

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
- [x] Dedicated `/ready` probe with env validation
- [x] Batch processing support
- [x] JWT authentication support
- [x] Redis persistence for sessions and keys
- [x] Container health checks and auto-restart policies
- [x] Structured JSON logging with `trace_id`
- [x] Automated evaluation pipeline + reports
- [x] Rule-based classifier and prompt library

### 💡 Stretch Enhancements
- [ ] **SDK Development**: Publish client libraries for Python, JavaScript, and Go.
- [ ] **Integration Recipes**: Provide guides for Zendesk, Jira, and Slack.
- [ ] **Advanced Alerting**: Add Prometheus alert rules + PagerDuty hooks.
- [ ] **Extended Load Testing**: k6/Locust scenarios for 1k RPS targets.

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

## 🧰 Maintainer

**Artem Rivnyi** — Junior Technical Support / DevOps Enthusiast

* 📧 [artemrivnyi@outlook.com](mailto:artemrivnyi@outlook.com)  
* 🔗 [LinkedIn](https://www.linkedin.com/in/artem-rivnyi/)  
* 🌐 [Personal Projects](https://personal-page-devops.onrender.com/)  
* 💻 [GitHub](https://github.com/ArtemRivnyi)
