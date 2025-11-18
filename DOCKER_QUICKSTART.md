# 🐳 Docker Quick Start Guide

## Prerequisites
- Docker and Docker Compose installed
- Google Gemini API key

## Quick Start

### 1. Create Environment File

```bash
cp .env.example .env
```

Edit `.env` and add:
```env
GEMINI_API_KEY=your_gemini_api_key_here
SECRET_KEY=your_secret_key_min_32_chars
JWT_SECRET=your_jwt_secret_or_same_as_secret_key
```

### 2. Start Services

```bash
# Start all services (app, redis, prometheus, grafana)
docker-compose up -d

# View logs
docker-compose logs -f app

# Check status
docker-compose ps
```

### 3. Verify Installation

```bash
# Health check
curl http://localhost:5000/api/v1/health

# API documentation
open http://localhost:5000/api-docs

# Grafana dashboards
open http://localhost:3000
# Default: admin/admin
```

### 4. Stop Services

```bash
docker-compose down
```

## Production Deployment

For production, use `docker-compose.prod.yml`:

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Troubleshooting

- **Port conflicts**: Change ports in `docker-compose.yml`
- **Redis connection**: Ensure Redis container is healthy
- **API key errors**: Check `.env` file has correct `GEMINI_API_KEY`
- **Build errors**: Ensure Python 3.12 is used in Dockerfile

See [docs/DOCKER_TROUBLESHOOTING.md](docs/DOCKER_TROUBLESHOOTING.md) for more details.

