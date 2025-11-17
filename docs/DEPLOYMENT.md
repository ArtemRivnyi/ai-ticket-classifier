# Deployment Guide

## Docker Deployment

### Production (Simplified - Recommended)
```bash
# Start without PostgreSQL (optional)
docker-compose -f docker-compose.simple.prod.yml up -d
```

### Production (Full - with PostgreSQL)
```bash
# Requires PostgreSQL to be healthy
docker-compose -f docker-compose.prod.yml up -d
```

### Development
```bash
docker-compose up -d
```

### Troubleshooting
If PostgreSQL fails, use simplified version:
```bash
docker-compose -f docker-compose.simple.prod.yml up -d
```

See [DOCKER_TROUBLESHOOTING.md](DOCKER_TROUBLESHOOTING.md) for more help.

## Environment Variables

Required:
- `GEMINI_API_KEY` - Google Gemini API key
- `MASTER_API_KEY` - Master API key for admin access

Optional:
- `OPENAI_API_KEY` - OpenAI API key (for fallback)
- `REDIS_URL` - Redis connection URL
- `DATABASE_URL` - PostgreSQL connection URL
- `FLASK_ENV` - Environment (production/development)

## Health Checks

```bash
curl http://localhost:5000/api/v1/health
```

## Monitoring

- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000
- Metrics: http://localhost:5000/metrics

