# Docker Troubleshooting Guide

## Common Issues

### PostgreSQL Container Unhealthy

**Problem:** `container ai-ticket-classifier-postgres is unhealthy`

**Solution:** PostgreSQL is optional. Use simplified compose file:

```bash
docker-compose -f docker-compose.simple.prod.yml up -d
```

Or remove PostgreSQL dependency from `docker-compose.prod.yml` if not needed.

### Redis Connection Failed

**Problem:** `Error 11001 connecting to redis:6379`

**Solution:** 
- Redis is optional - application uses in-memory fallback
- For production, ensure Redis container is running:
  ```bash
  docker-compose up -d redis
  ```

### Gemini Provider Not Available (Wrong Python Version)

**Problem:** `Metaclasses with custom tp_new are not supported`

**Solution:**
- Use Python 3.12 in Docker (required, already configured)
- Or set `OPENAI_API_KEY` for fallback provider

### Health Check Fails

**Problem:** Container health check fails

**Solution:**
- Ensure application is running: `docker-compose logs app`
- Check if port 5000 is accessible
- Verify environment variables are set

## Quick Fixes

### Start Without PostgreSQL
```bash
docker-compose -f docker-compose.simple.prod.yml up -d
```

### Start Only Required Services
```bash
docker-compose up -d redis app
```

### Check Logs
```bash
docker-compose logs -f app
docker-compose logs -f redis
```

### Restart Services
```bash
docker-compose restart app
docker-compose restart redis
```

### Clean Start
```bash
docker-compose down -v
docker-compose up -d
```

