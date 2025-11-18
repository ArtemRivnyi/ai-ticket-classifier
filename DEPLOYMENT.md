# 🚀 Deployment Guide

## Production Deployment with Docker

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+
- Google Gemini API key

### Step 1: Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your values
nano .env  # or use your preferred editor
```

Required variables:
```env
GEMINI_API_KEY=your_gemini_api_key
SECRET_KEY=your_secret_key_min_32_chars
JWT_SECRET=your_jwt_secret
```

### Step 2: Build and Start Services

```bash
# Build and start all services
docker-compose up -d --build

# Check service status
docker-compose ps

# View logs
docker-compose logs -f app
```

### Step 3: Verify Deployment

```bash
# Health check
curl http://localhost:5000/api/v1/health

# API documentation
curl http://localhost:5000/api-docs

# Metrics endpoint
curl http://localhost:5000/metrics
```

### Step 4: Access Monitoring

- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **API Docs**: http://localhost:5000/api-docs

## Production Configuration

For production, use `docker-compose.prod.yml`:

```bash
docker-compose -f docker-compose.prod.yml up -d
```

This includes:
- Resource limits
- Extended retention for Prometheus
- `restart: always` policy

## Health Checks

All services include health checks:
- **App**: `/api/v1/health` endpoint
- **Redis**: `redis-cli ping`
- **Prometheus**: Built-in health endpoint
- **Grafana**: Built-in health endpoint

## Scaling

To scale the application:

```bash
docker-compose up -d --scale app=3
```

Note: Update Gunicorn workers in Dockerfile for better performance.

## Backup

Redis data is persisted in Docker volume:
```bash
# Backup Redis data
docker exec ai-ticket-redis redis-cli SAVE
docker cp ai-ticket-redis:/data/dump.rdb ./backup/
```

## Troubleshooting

See [docs/DOCKER_TROUBLESHOOTING.md](docs/DOCKER_TROUBLESHOOTING.md) for common issues.

