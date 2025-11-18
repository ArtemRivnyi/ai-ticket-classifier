# 🚂 Railway Deployment Guide

## Quick Deploy to Railway

### Prerequisites
- GitHub repository pushed to `GEMINI_API_PROD_READY` branch
- Railway account (free $5/month credit)
- Google Gemini API key

---

## 🚀 One-Click Deploy

### Step 1: Push to GitHub
```bash
git push origin GEMINI_API_PROD_READY
```

### Step 2: Deploy via Railway

1. **Go to Railway:**
   - Visit [railway.app](https://railway.app/)
   - Click "Start a New Project"

2. **Deploy from GitHub:**
   - Click "Deploy from GitHub repo"
   - Select your repository: `ArtemRivnyi/ai-ticket-classifier`
   - Select branch: `GEMINI_API_PROD_READY`
   - Click "Deploy Now"

3. **Railway Auto-Detects:**
   - ✅ Python 3.12
   - ✅ `railway.json` configuration
   - ✅ `requirements.txt` dependencies
   - ✅ Gunicorn start command

### Step 3: Add Redis Service

1. **In your Railway project:**
   - Click "+ New"
   - Select "Database" → "Add Redis"
   - Railway automatically creates `REDIS_URL` variable

### Step 4: Configure Environment Variables

Click on your Flask service → "Variables" tab:

```bash
# Required
GEMINI_API_KEY=<your-gemini-api-key>
MASTER_API_KEY=<your-master-api-key>
SECRET_KEY=<generate-random-string>

# Auto-configured
REDIS_URL=redis://redis.railway.internal:6379
PORT=5000

# Pre-configured (already set)
PYTHON_VERSION=3.12.0
FLASK_ENV=production
FORCE_HTTPS=true
CORS_ORIGINS=*
```

### Step 5: Generate Domain

1. **In your Flask service:**
   - Go to "Settings" tab
   - Scroll to "Networking"
   - Click "Generate Domain"
   - You'll get: `https://your-app.up.railway.app`

---

## ✅ Verify Deployment

Once deployed, test your endpoints:

```bash
# Set your Railway URL
export RAILWAY_URL="https://your-app.up.railway.app"

# Health check
curl $RAILWAY_URL/api/v1/health

# API docs
open $RAILWAY_URL/api-docs

# Register API key
curl -X POST $RAILWAY_URL/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -H "X-Forwarded-Proto: https" \
  -d '{
    "email": "test@example.com",
    "name": "Test User",
    "organization": "Test Org"
  }'

# Classify ticket
curl -X POST $RAILWAY_URL/api/v1/classify \
  -H "Content-Type: application/json" \
  -H "X-API-Key: <your-api-key>" \
  -H "X-Forwarded-Proto: https" \
  -d '{"ticket": "VPN connection keeps dropping"}'
```

---

## 📊 Monitoring

Railway provides built-in monitoring:

### Logs
```bash
# Real-time logs
Railway Dashboard → Service → Deployments → View Logs
```

### Metrics
```bash
# CPU, Memory, Network
Railway Dashboard → Service → Metrics
```

### Custom Metrics
```bash
# Prometheus endpoint
curl $RAILWAY_URL/metrics
```

---

## 💰 Cost Estimate

Railway offers **$5 free credit per month**:

| Resource | Usage | Cost |
|----------|-------|------|
| Flask App | ~$3-5/month | Included in free tier |
| Redis | ~$1-2/month | Included in free tier |
| **Total** | | **$0** (within free tier) |

### Scaling Costs
- **Hobby Plan**: $5/month (500 hours)
- **Pro Plan**: $20/month (unlimited)

---

## 🔧 Advanced Configuration

### Custom Domain

1. **Add Custom Domain:**
   ```bash
   Railway Dashboard → Service → Settings → Custom Domain
   Add: api.yourdomain.com
   ```

2. **Configure DNS:**
   ```bash
   # Add CNAME record
   CNAME api.yourdomain.com → your-app.up.railway.app
   ```

### Auto-Deploy on Push

Railway automatically deploys when you push to `GEMINI_API_PROD_READY`:

```bash
git add .
git commit -m "feat: new feature"
git push origin GEMINI_API_PROD_READY
# Railway auto-deploys in ~2-3 minutes
```

### Rollback

```bash
# Railway Dashboard → Service → Deployments
- Click on previous successful deployment
- Click "Redeploy"
```

### Scaling

#### Horizontal Scaling
```bash
# Railway Dashboard → Service → Settings
- Replicas: 1-10 instances
- Auto-scaling: Available on Pro plan
```

#### Vertical Scaling
```bash
# Railway automatically scales resources
- Memory: Up to 8GB
- CPU: Up to 8 vCPUs
```

---

## 🐛 Troubleshooting

### Service won't start
```bash
# Check logs
Railway Dashboard → Service → Deployments → View Logs

# Common issues:
- Missing environment variables
- Python version mismatch
- Port binding issues
```

### 403 Forbidden errors
```bash
# Ensure X-Forwarded-Proto header
curl -H "X-Forwarded-Proto: https" $RAILWAY_URL/api/v1/health
```

### Redis connection errors
```bash
# Verify REDIS_URL
Railway Dashboard → Service → Variables → REDIS_URL

# Should be: redis://redis.railway.internal:6379
```

### Out of memory
```bash
# Upgrade to Pro plan or optimize:
- Reduce worker count in gunicorn
- Enable Redis maxmemory-policy
- Optimize database queries
```

---

## 🚀 CI/CD Pipeline

Railway provides automatic CI/CD:

```bash
# .github/workflows/railway-deploy.yml (optional)
name: Railway Deploy
on:
  push:
    branches: [GEMINI_API_PROD_READY]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Railway
        run: echo "Railway auto-deploys on push"
```

---

## 📈 Performance Optimization

### Enable Caching
```bash
# Already configured via Redis
REDIS_URL=redis://redis.railway.internal:6379
```

### Optimize Workers
```bash
# railway.json
"startCommand": "gunicorn --bind 0.0.0.0:$PORT --workers 4 --timeout 120 app:app"

# Adjust workers based on traffic:
- Low traffic: 2 workers
- Medium traffic: 4 workers
- High traffic: 8 workers
```

### Enable Compression
```bash
# Add to app.py
from flask_compress import Compress
compress = Compress(app)
```

---

## 🔒 Security Best Practices

### Environment Variables
```bash
# Never commit secrets
# Use Railway's Variables tab for:
- GEMINI_API_KEY
- MASTER_API_KEY
- SECRET_KEY
```

### HTTPS Only
```bash
# Already enforced
FORCE_HTTPS=true
```

### Rate Limiting
```bash
# Already configured via Redis
# Adjust limits in app.py if needed
```

---

## 📚 Next Steps

After deployment:
1. ✅ Test all endpoints
2. ✅ Monitor logs and metrics
3. ✅ Set up custom domain (optional)
4. ✅ Configure alerts (optional)
5. ✅ Scale as needed

---

## 🆘 Support

- **Railway Docs**: [docs.railway.app](https://docs.railway.app/)
- **Railway Discord**: [discord.gg/railway](https://discord.gg/railway)
- **Project Issues**: [GitHub Issues](https://github.com/ArtemRivnyi/ai-ticket-classifier/issues)

---

**Deployment Time:** ~5 minutes  
**Status:** ✅ Production Ready  
**Cost:** $0 (free tier)
