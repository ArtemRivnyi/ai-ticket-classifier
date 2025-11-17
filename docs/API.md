# API Documentation

Complete API reference for AI Ticket Classifier.

## Base URL

```
http://localhost:5000/api/v1
```

## Authentication

All endpoints (except `/health`) require API key authentication:

```
X-API-Key: your_api_key_here
```

## Endpoints

### Health Check
```
GET /api/v1/health
```

### Classify Ticket
```
POST /api/v1/classify
```

### Batch Classification
```
POST /api/v1/batch
```

### Webhooks
```
POST /api/v1/webhooks
```

### Authentication
```
POST /api/v1/auth/register
GET /api/v1/auth/keys
POST /api/v1/auth/keys
DELETE /api/v1/auth/keys/{key_id}
GET /api/v1/auth/usage
POST /api/v1/auth/jwt/login
```

For detailed API documentation, visit `/api-docs` when the server is running.

