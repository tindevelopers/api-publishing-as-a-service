# Docker Deployment Guide

This guide covers deploying the AI Content Publisher API using Docker in various environments.

## 🐳 Docker Images

The project includes multiple Docker configurations:

- **`Dockerfile`** - Standard single-stage build for development
- **`Dockerfile.prod`** - Multi-stage production build (optimized)
- **`docker-compose.yml`** - Local development with all services
- **`docker-compose.prod.yml`** - Production deployment with scaling

## 🚀 Quick Start

### Local Development

1. **Clone and setup**
   ```bash
   git clone <repository-url>
   cd api-publishing-as-a-service
   cp .env.example .env
   # Edit .env with your configuration
   ```

2. **Start all services**
   ```bash
   docker-compose up -d
   ```

3. **Access the API**
   - API: http://localhost:8080
   - Docs: http://localhost:8080/docs
   - Health: http://localhost:8080/health

### Production Deployment

1. **Setup production environment**
   ```bash
   cp env.prod.example .env.prod
   # Edit .env.prod with your production values
   ```

2. **Deploy with production compose**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

## 📦 Docker Build Options

### Standard Build
```bash
# Build development image
docker build -t ai-content-publisher:dev .

# Run locally
docker run -p 8080:8080 --env-file .env ai-content-publisher:dev
```

### Production Build
```bash
# Build production image (multi-stage, optimized)
docker build -f Dockerfile.prod -t ai-content-publisher:prod .

# Run production image
docker run -p 8080:8080 --env-file .env.prod ai-content-publisher:prod
```

## 🏗️ Docker Compose Services

### Development Stack
- **api** - FastAPI application
- **redis** - Caching and task queue
- **postgres** - Database
- **celery-worker** - Background task processing
- **celery-beat** - Scheduled tasks

### Production Stack
- **api** - FastAPI application (with resource limits)
- **redis** - Caching and task queue
- **postgres** - Database
- **celery-worker** - Background workers (scaled)
- **celery-beat** - Scheduled tasks
- **nginx** - Reverse proxy (optional)

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `SECRET_KEY` | API authentication key | Yes | - |
| `ENVIRONMENT` | Environment (development/production) | Yes | development |
| `DEBUG` | Enable debug mode | No | false |
| `LOG_LEVEL` | Logging level | No | INFO |
| `DATABASE_URL` | PostgreSQL connection string | Yes | - |
| `REDIS_URL` | Redis connection string | Yes | - |

### Platform Configuration

Configure your platform credentials in the environment file:

```bash
# Webflow
WEBFLOW_API_KEY=your-api-key
WEBFLOW_SITE_ID=your-site-id

# WordPress
WORDPRESS_SITE_URL=https://yoursite.com
WORDPRESS_USERNAME=your-username
WORDPRESS_APP_PASSWORD=your-app-password

# LinkedIn
LINKEDIN_ACCESS_TOKEN=your-access-token

# Twitter
TWITTER_API_KEY=your-api-key
TWITTER_API_SECRET=your-api-secret
```

## 🚀 Deployment Strategies

### 1. Single Container Deployment

```bash
# Build and run single container
docker build -t ai-content-publisher .
docker run -d \
  --name ai-content-publisher \
  -p 8080:8080 \
  --env-file .env \
  --restart unless-stopped \
  ai-content-publisher
```

### 2. Docker Compose Deployment

```bash
# Development
docker-compose up -d

# Production
docker-compose -f docker-compose.prod.yml up -d

# Scale workers
docker-compose -f docker-compose.prod.yml up -d --scale celery-worker=3
```

### 3. Docker Swarm Deployment

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.prod.yml ai-content-publisher

# Scale services
docker service scale ai-content-publisher_celery-worker=3
```

### 4. Kubernetes Deployment

```bash
# Convert compose to k8s manifests
kompose convert -f docker-compose.prod.yml

# Deploy to Kubernetes
kubectl apply -f .
```

## 🔍 Monitoring and Health Checks

### Health Endpoints
- `GET /health` - Basic health check
- `GET /health/ready` - Readiness check
- `GET /health/live` - Liveness check
- `GET /metrics` - Prometheus metrics

### Docker Health Checks
```dockerfile
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1
```

### Monitoring Commands
```bash
# Check container health
docker ps
docker inspect <container-id> | grep Health

# View logs
docker-compose logs -f api
docker-compose logs -f celery-worker

# Monitor metrics
curl http://localhost:8080/metrics
```

## 🛠️ Development Workflow

### Local Development
```bash
# Start development environment
docker-compose up -d

# View logs
docker-compose logs -f

# Execute commands in container
docker-compose exec api bash
docker-compose exec api python -m pytest

# Rebuild after changes
docker-compose up -d --build
```

### Testing
```bash
# Run tests in container
docker-compose exec api pytest

# Run tests with coverage
docker-compose exec api pytest --cov=app

# Run specific test
docker-compose exec api pytest tests/test_publisher.py
```

## 🔒 Security Considerations

### Production Security
- Use non-root user in containers
- Set resource limits
- Use secrets management
- Enable HTTPS with reverse proxy
- Regular security updates

### Environment Security
```bash
# Use Docker secrets
echo "your-secret-key" | docker secret create api_secret_key -

# Use Docker configs
docker config create api_config .env.prod
```

## 📊 Performance Optimization

### Resource Limits
```yaml
deploy:
  resources:
    limits:
      memory: 1G
      cpus: '1.0'
    reservations:
      memory: 512M
      cpus: '0.5'
```

### Scaling
```bash
# Scale API instances
docker-compose -f docker-compose.prod.yml up -d --scale api=3

# Scale workers
docker-compose -f docker-compose.prod.yml up -d --scale celery-worker=5
```

## 🐛 Troubleshooting

### Common Issues

1. **Container won't start**
   ```bash
   # Check logs
   docker-compose logs api
   
   # Check environment variables
   docker-compose exec api env
   ```

2. **Database connection issues**
   ```bash
   # Check database status
   docker-compose exec postgres pg_isready
   
   # Check database logs
   docker-compose logs postgres
   ```

3. **Redis connection issues**
   ```bash
   # Check Redis status
   docker-compose exec redis redis-cli ping
   
   # Check Redis logs
   docker-compose logs redis
   ```

### Debug Commands
```bash
# Enter container shell
docker-compose exec api bash

# Check running processes
docker-compose exec api ps aux

# Check network connectivity
docker-compose exec api curl -f http://postgres:5432
docker-compose exec api curl -f http://redis:6379
```

## 📈 Production Checklist

- [ ] Environment variables configured
- [ ] Secrets properly managed
- [ ] Resource limits set
- [ ] Health checks configured
- [ ] Logging configured
- [ ] Monitoring enabled
- [ ] Backup strategy in place
- [ ] SSL/TLS configured
- [ ] Firewall rules configured
- [ ] Regular updates scheduled

## 🔄 CI/CD Integration

### GitHub Actions Example
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
      - name: Build and deploy
        run: |
          docker build -f Dockerfile.prod -t ai-content-publisher .
          docker-compose -f docker-compose.prod.yml up -d
```

This Docker setup provides a robust, scalable foundation for deploying the AI Content Publisher API in any environment.
