# API Publishing as a Service

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/tindevelopers/api-publishing-as-a-service)
[![Python](https://img.shields.io/badge/python-3.11+-green.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-red.svg)](https://fastapi.tiangolo.com)
[![Google Cloud Run](https://img.shields.io/badge/Google%20Cloud%20Run-Ready-orange.svg)](https://cloud.google.com/run)

A comprehensive **Publishing as a Service** platform that enables seamless publishing of AI-generated content to multiple content management systems and social platforms. Built with Python FastAPI and designed for enterprise-scale deployment on Google Cloud Run.

**Version 1.0.0** - Initial release with full multi-platform publishing capabilities.

## 🚀 What is API Publishing as a Service?

This service acts as a unified publishing layer that allows you to distribute content across multiple platforms simultaneously. Whether you're managing a content marketing campaign, publishing blog posts, or distributing social media content, this API provides a single interface to reach all your publishing destinations.

## 🎯 Supported Platforms

### Content Management Systems
- **Webflow** - Modern website builder with CMS
- **WordPress** - World's most popular CMS
- **LinkedIn** - Professional social networking
- **Twitter/X** - Social media microblogging

### Content Types Supported
- **Blog Posts** - Long-form articles and posts
- **FAQ Content** - Question and answer formats
- **Product Descriptions** - E-commerce content
- **Landing Pages** - Marketing and conversion pages
- **Articles** - News and editorial content

## ✨ Key Features

### 🎯 Core Publishing Features
- **Multi-Platform Publishing**: Simultaneously publish to Webflow, WordPress, LinkedIn, and Twitter
- **Content Validation**: Comprehensive validation with SEO scoring and platform-specific checks
- **Batch Processing**: Efficient bulk publishing with configurable concurrency
- **Content Scheduling**: Schedule content for future publishing
- **Platform Testing**: Test platform connections and content compatibility

### 🔧 Advanced Features
- **Content Optimization**: Automatic SEO optimization and meta tag generation
- **Image Processing**: Handle and optimize images for different platforms
- **Error Handling**: Robust error handling with detailed error reporting
- **Retry Logic**: Automatic retry mechanisms for failed publishes
- **Rate Limiting**: Built-in rate limiting to respect platform APIs

### 📊 Monitoring & Analytics
- **Real-time Monitoring**: Prometheus metrics and structured logging
- **Health Checks**: Comprehensive health monitoring for all services
- **Performance Metrics**: Track publishing performance and success rates
- **Audit Logging**: Complete audit trail of all publishing activities

### 🏗️ Architecture & Scalability
- **Microservices Architecture**: Modular, scalable design
- **Async Processing**: High-performance async/await implementation
- **Auto-scaling**: Designed for Google Cloud Run with automatic scaling
- **Type Safety**: Full Pydantic models with comprehensive validation
- **Docker Ready**: Complete containerization with multi-stage builds

## Quick Start

### Prerequisites

- Python 3.11+
- Google Cloud CLI
- Docker
- Node.js 22+ (for MCP tools)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd api-publishing-as-a-service
   ```

2. **Set up environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run locally**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
   ```

## 🚀 Google Cloud Run Deployment

This service is specifically designed for deployment on Google Cloud Run, providing automatic scaling, serverless architecture, and enterprise-grade reliability.

### Prerequisites for Google Cloud Run
- Google Cloud Project with billing enabled
- Google Cloud CLI installed and authenticated
- Docker installed locally
- Required APIs enabled (Cloud Run, Container Registry, Cloud Build)

### Quick Deployment

1. **Set up Google Cloud**
   ```bash
   # Authenticate with Google Cloud
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   
   # Enable required APIs
   gcloud services enable run.googleapis.com
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable containerregistry.googleapis.com
   ```

2. **Configure Environment Variables**
   ```bash
   # Copy and edit environment file
   cp .env.example .env
   # Edit .env with your platform credentials
   ```

3. **Deploy using the automated script**
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

### Manual Deployment

1. **Build and push Docker image**
   ```bash
   # Build production image
   docker build -f Dockerfile.prod -t gcr.io/YOUR_PROJECT_ID/api-publishing-service .
   
   # Push to Google Container Registry
   docker push gcr.io/YOUR_PROJECT_ID/api-publishing-service
   ```

2. **Deploy to Cloud Run**
   ```bash
   gcloud run deploy api-publishing-service \
     --image gcr.io/YOUR_PROJECT_ID/api-publishing-service \
     --region us-central1 \
     --platform managed \
     --allow-unauthenticated \
     --port 8080 \
     --memory 1Gi \
     --cpu 1 \
     --min-instances 0 \
     --max-instances 10 \
     --concurrency 80 \
     --timeout 300 \
     --set-env-vars ENVIRONMENT=production
   ```

### Production Configuration

For production deployment, ensure you have:

- **Environment Variables**: All platform credentials configured
- **Resource Limits**: Appropriate memory and CPU allocation
- **Scaling Configuration**: Min/max instances set for your traffic
- **Security**: Authentication and authorization configured
- **Monitoring**: Cloud Monitoring and Logging enabled

### Cost Optimization

Google Cloud Run pricing is based on:
- **Request count**: Number of API calls
- **Compute time**: CPU and memory usage
- **Network egress**: Data transfer

Optimize costs by:
- Setting appropriate min/max instances
- Using efficient memory allocation
- Implementing proper caching
- Monitoring usage with Cloud Monitoring

## API Documentation

Once deployed, access the interactive API documentation at:
- **Swagger UI**: `https://your-service-url/docs`
- **ReDoc**: `https://your-service-url/redoc`

## Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `SECRET_KEY` | Secret key for authentication | Yes | - |
| `WEBFLOW_API_KEY` | Webflow API key | No | - |
| `WEBFLOW_SITE_ID` | Webflow site ID | No | - |
| `WORDPRESS_SITE_URL` | WordPress site URL | No | - |
| `WORDPRESS_USERNAME` | WordPress username | No | - |
| `WORDPRESS_PASSWORD` | WordPress password/app password | No | - |
| `LINKEDIN_ACCESS_TOKEN` | LinkedIn access token | No | - |
| `TWITTER_API_KEY` | Twitter API key | No | - |
| `TWITTER_API_SECRET` | Twitter API secret | No | - |
| `TWITTER_ACCESS_TOKEN` | Twitter access token | No | - |
| `TWITTER_ACCESS_TOKEN_SECRET` | Twitter access token secret | No | - |

### Platform Setup

#### Webflow
1. Go to [Webflow Integrations](https://webflow.com/integrations)
2. Create a new integration
3. Get your API key and site ID
4. Set environment variables

#### WordPress
1. Enable WordPress REST API
2. Create an application password
3. Set environment variables

#### LinkedIn
1. Create a LinkedIn app
2. Get access token
3. Set environment variables

#### Twitter
1. Create a Twitter app
2. Get API keys and tokens
3. Set environment variables

## API Usage

### Authentication

All publishing endpoints require authentication. Include the secret key in the Authorization header:

```bash
curl -H "Authorization: Bearer YOUR_SECRET_KEY" \
     -H "Content-Type: application/json" \
     -X POST https://your-service-url/content/publish \
     -d '{"content": {...}, "platforms": ["webflow"]}'
```

### Publishing Content

#### Single Content Publishing

```python
import requests

url = "https://your-service-url/content/publish"
headers = {
    "Authorization": "Bearer YOUR_SECRET_KEY",
    "Content-Type": "application/json"
}

data = {
    "content": {
        "type": "blog",
        "title": "AI Content Creation Guide",
        "content": "<h1>Introduction</h1><p>This is a comprehensive guide...</p>",
        "excerpt": "Learn how to create AI-generated content",
        "tags": ["AI", "Content", "Guide"],
        "categories": ["Technology"],
        "status": "published",
        "seo": {
            "meta_title": "AI Content Creation Guide - Best Practices",
            "meta_description": "Learn the best practices for creating AI-generated content",
            "keywords": ["ai content", "content creation", "automation"]
        }
    },
    "platforms": ["webflow", "wordpress"]
}

response = requests.post(url, json=data, headers=headers)
print(response.json())
```

#### Batch Publishing

```python
data = {
    "content_items": [
        {
            "type": "blog",
            "title": "Post 1",
            "content": "Content 1...",
            "status": "published"
        },
        {
            "type": "blog", 
            "title": "Post 2",
            "content": "Content 2...",
            "status": "published"
        }
    ],
    "platforms": ["webflow", "wordpress"],
    "concurrency": 2
}

response = requests.post("https://your-service-url/content/batch-publish", 
                        json=data, headers=headers)
```

### Content Validation

```python
# Validate content before publishing
validation_data = {
    "type": "blog",
    "title": "My Blog Post",
    "content": "<p>This is my content</p>"
}

response = requests.post("https://your-service-url/content/validate",
                        json=validation_data, headers=headers)
validation_result = response.json()

if validation_result["is_valid"]:
    print(f"Content is valid with score: {validation_result['score']}")
else:
    print("Validation errors:", validation_result["errors"])
```

## Monitoring

### Health Checks

- **Basic Health**: `GET /health`
- **Readiness**: `GET /health/ready`
- **Liveness**: `GET /health/live`

### Metrics

Prometheus metrics are available at `/metrics`:

- `content_published_total` - Total content published by platform
- `content_publish_duration_seconds` - Publishing duration
- `http_requests_total` - HTTP request metrics
- `platform_connection_tests_total` - Platform connection tests

### Logging

The API uses structured logging with the following levels:
- `INFO` - General information
- `WARNING` - Warnings and non-critical issues
- `ERROR` - Errors and failures
- `DEBUG` - Detailed debugging information

## Development

### Running Tests

```bash
pytest tests/ -v --cov=app
```

### Code Quality

```bash
# Format code
black app/

# Sort imports
isort app/

# Lint code
flake8 app/

# Type checking
mypy app/
```

### Local Development with Docker

```bash
# Build image
docker build -t ai-content-publisher .

# Run container
docker run -p 8080:8080 --env-file .env ai-content-publisher
```

## Architecture

### Components

- **FastAPI Application**: Main API server
- **Content Publisher Service**: Core publishing logic
- **Platform Services**: Platform-specific implementations
- **Validation Service**: Content validation and SEO optimization
- **Monitoring**: Metrics, logging, and health checks

### Data Flow

1. **Request Validation**: Validate incoming requests
2. **Content Validation**: Validate content structure and SEO
3. **Platform Publishing**: Publish to specified platforms
4. **Response Aggregation**: Combine results from all platforms
5. **Metrics Collection**: Record metrics and logs

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

- 📚 [API Documentation](https://your-service-url/docs)
- 🐛 [Report Issues](https://github.com/your-repo/issues)
- 💬 [Discord Community](https://discord.gg/your-community)

---

Built with ❤️ for the AI content creation community.
