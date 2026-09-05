# Deployment Guide - AI Meeting Insights Dashboard

## 🌐 Production Deployment

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                     End User                             │
└────────────────────────┬────────────────────────────────┘
                         │
        ┌────────────────┴────────────────┐
        ▼                                  ▼
   ┌─────────────────┐           ┌──────────────────┐
   │  Frontend (SPA) │           │  CDN / S3 (Optional)
   │  - React        │           │  Static Assets   │
   │  - Vite Build   │           └──────────────────┘
   │  - Tailwind CSS │
   └────────┬────────┘
            │ API Calls (HTTPS)
            ▼
   ┌────────────────────┐
   │  Load Balancer     │
   │  (Optional)        │
   └────────┬───────────┘
            │
        ┌───┴────┐
        ▼        ▼
   ┌─────────────────┐    ┌──────────────────┐
   │  Backend Inst 1 │    │  Backend Inst 2  │
   │  FastAPI        │    │  FastAPI         │
   └────────┬────────┘    └────────┬─────────┘
            │                      │
            └──────────┬───────────┘
                       ▼
            ┌────────────────────┐
            │   Database         │
            │   (PostgreSQL)     │
            └────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
   ┌─────────────┐ ┌────────────┐ ┌─────────────┐
   │  File       │ │  Redis     │ │  S3         │
   │  Storage    │ │  (Cache)   │ │  (Uploads)  │
   └─────────────┘ └────────────┘ └─────────────┘
```

---

## 🐳 Docker Deployment

### Backend Dockerfile

Create `backend/Dockerfile`:

```dockerfile
FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/health')"

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Dockerfile

Create `frontend/Dockerfile`:

```dockerfile
# Build stage
FROM node:16-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Production stage
FROM node:16-alpine

WORKDIR /app

# Install lightweight HTTP server
RUN npm install -g serve

# Copy built app from builder
COPY --from=builder /app/dist ./dist

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:3000 || exit 1

CMD ["serve", "-s", "dist", "-l", "3000"]
```

### Docker Compose Setup

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: meeting-insights-backend
    ports:
      - "8000:8000"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - GEMINI_MODEL=gemini-2.5-flash
      - BACKEND_URL=http://backend:8000
      - FRONTEND_URL=http://frontend:3000
      - DATABASE_URL=postgresql://user:password@db:5432/meeting_db
    volumes:
      - ./backend/uploads:/app/uploads
      - ./backend/temp:/app/temp
    depends_on:
      - db
      - redis
    networks:
      - meeting-network
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: meeting-insights-frontend
    ports:
      - "3000:3000"
    environment:
      - VITE_API_BASE_URL=http://backend:8000
    depends_on:
      - backend
    networks:
      - meeting-network
    restart: unless-stopped

  db:
    image: postgres:15-alpine
    container_name: meeting-insights-db
    environment:
      - POSTGRES_DB=meeting_db
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=securepassword
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - meeting-network
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: meeting-insights-cache
    ports:
      - "6379:6379"
    networks:
      - meeting-network
    restart: unless-stopped

volumes:
  postgres_data:

networks:
  meeting-network:
    driver: bridge
```

### Build and Deploy

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## ☁️ Cloud Deployment Options

### Option 1: AWS Deployment

#### Using AWS Elastic Beanstalk

```bash
# Install EB CLI
pip install awsebcli

# Initialize EB application
eb init -p docker meeting-insights-api

# Create environment
eb create production

# Deploy
eb deploy

# View logs
eb logs
```

#### Using AWS ECS + Fargate

```bash
# Create ECS cluster
aws ecs create-cluster --cluster-name meeting-insights

# Create task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json

# Create service
aws ecs create-service \
  --cluster meeting-insights \
  --service-name api \
  --task-definition meeting-insights-api \
  --desired-count 2
```

#### Using AWS Lambda (Serverless)

Note: Lambda has 15-minute timeout limit, not ideal for long transcriptions.

### Option 2: Google Cloud Run

```bash
# Build and push to Container Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/meeting-insights-api

# Deploy to Cloud Run
gcloud run deploy meeting-insights-api \
  --image gcr.io/PROJECT_ID/meeting-insights-api \
  --platform managed \
  --region us-central1 \
  --set-env-vars GEMINI_API_KEY=your-gemini-api-key
```

### Option 3: Heroku Deployment

Create `Procfile`:

```
web: cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Deploy:

```bash
# Install Heroku CLI
brew install heroku/brew/heroku

# Login
heroku login

# Create app
heroku create meeting-insights-api

# Set environment variables
heroku config:set GEMINI_API_KEY=your-gemini-api-key

# Deploy
git push heroku main

# View logs
heroku logs --tail
```

### Option 4: Azure Container Instances

```bash
# Create resource group
az group create --name meeting-insights --location eastus

# Create container registry
az acr create --resource-group meeting-insights \
  --name meetinginsights --sku Basic

# Build and push
az acr build --registry meetinginsights \
  --image meeting-insights-api:latest .

# Deploy container
az container create \
  --resource-group meeting-insights \
  --name meeting-insights-api \
  --image meetinginsights.azurecr.io/meeting-insights-api:latest \
  --cpu 2 --memory 3.5
```

---

## 🔐 Security Best Practices

### Environment Variables

Use a secrets management service:

**AWS Secrets Manager:**
```bash
aws secretsmanager create-secret \
  --name meeting-insights/gemini-key \
  --secret-string 'sk-...'
```

**Google Secret Manager:**
```bash
echo -n 'your-gemini-api-key' | gcloud secrets create gemini-key --data-file=-
```

**Azure Key Vault:**
```bash
az keyvault secret set \
  --vault-name meeting-insights \
  --name gemini-key \
  --value 'sk-...'
```

### SSL/TLS Certificate

Using Let's Encrypt with Nginx:

```nginx
server {
    listen 443 ssl http2;
    server_name api.meetinginsights.com;

    ssl_certificate /etc/letsencrypt/live/api.meetinginsights.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.meetinginsights.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8000;
    }
}
```

### Database Security

- Use managed database services (RDS, Cloud SQL, etc.)
- Enable encryption at rest and in transit
- Use strong passwords
- Restrict network access
- Regular backups

### API Rate Limiting

Add to FastAPI:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/meetings/upload")
@limiter.limit("5/minute")
async def upload_meeting(request: Request, file: UploadFile = File(...)):
    ...
```

---

## 📊 Monitoring & Logging

### Application Monitoring

Add to `backend/app/main.py`:

```python
from pythonjsonlogger import jsonlogger
import logging

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

### Sentry Integration

```bash
pip install sentry-sdk
```

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="https://...@sentry.io/...",
    integrations=[FastApiIntegration()],
    traces_sample_rate=1.0,
)
```

### CloudWatch / Stackdriver

```python
import watchtower
import logging

logger = logging.getLogger(__name__)
logger.addHandler(watchtower.CloudWatchLogHandler())
```

---

## 🔄 Continuous Integration/Deployment

### GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Build and push Docker image
        uses: docker/build-push-action@v2
        with:
          push: true
          tags: your-registry/meeting-insights:latest
      
      - name: Deploy to Cloud Run
        uses: google-github-actions/deploy-cloudrun@v0
        with:
          service: meeting-insights-api
          image: your-registry/meeting-insights:latest
          region: us-central1
```

---

## 📈 Scaling Considerations

### Horizontal Scaling

1. **Multiple Backend Instances**
   - Use load balancer (ALB, Cloud Load Balancer, etc.)
   - Configure auto-scaling based on CPU/memory

2. **Database Scaling**
   - Use read replicas for reports
   - Implement connection pooling
   - Consider sharding for large datasets

3. **Caching Layer**
   - Use Redis for session management
   - Cache meeting results
   - Cache LLM responses

### Vertical Scaling

1. Increase machine resources (CPU, RAM)
2. Use faster GPU instances for transcription
3. Optimize code for memory usage

---

## 🚨 Disaster Recovery

### Backup Strategy

```bash
# Daily database backups
0 2 * * * pg_dump -h localhost meeting_db > /backups/db-$(date +\%Y\%m\%d).sql

# Upload to S3
aws s3 cp /backups/db-*.sql s3://backups/meeting-insights/

# Set retention policy
aws s3api put-bucket-lifecycle-configuration \
  --bucket backups \
  --lifecycle-configuration file://retention.json
```

### Failover Setup

1. Database replication (master-slave)
2. DNS failover to backup instance
3. Automatic health checks
4. Regular disaster recovery drills

---

## 📋 Pre-Production Checklist

- [ ] All environment variables configured
- [ ] API keys and secrets in secure storage
- [ ] SSL/TLS certificates installed
- [ ] Database backups configured
- [ ] Logging and monitoring enabled
- [ ] Rate limiting configured
- [ ] CORS properly configured
- [ ] Load testing completed
- [ ] Security scan completed
- [ ] Documentation updated
- [ ] Support plan defined
- [ ] Rollback procedure documented

---

## 🎯 Performance Optimization

### Backend Optimization

1. **Database Queries**
   - Add indexes on frequently queried columns
   - Use query optimization
   - Implement connection pooling

2. **Caching**
   - Cache LLM responses
   - Cache transcription results
   - Use Redis for session data

3. **Async Operations**
   - Use background jobs for long operations
   - Implement task queue (Celery, RQ)
   - Optimize I/O operations

### Frontend Optimization

1. **Bundle Size**
   - Lazy load components
   - Code splitting
   - Remove unused dependencies

2. **Caching**
   - Browser caching for static assets
   - Service workers for offline support
   - CDN for static files

---

## 📞 Support & Maintenance

### Regular Maintenance

- Weekly: Check logs and errors
- Monthly: Update dependencies
- Quarterly: Security audits
- Annually: Disaster recovery drill

### Monitoring Alerts

Set up alerts for:
- API response time > 5s
- Error rate > 1%
- Disk usage > 80%
- Database connection pool exhaustion
- Memory usage > 85%

---

**Last Updated**: August 31, 2026
