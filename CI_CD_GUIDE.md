# CI/CD Pipeline Guide

This guide explains the complete CI/CD pipeline for the API Publishing as a Service, including GitHub Actions workflows, deployment strategies, and best practices.

## 🚀 Pipeline Overview

The CI/CD pipeline consists of multiple workflows that handle different aspects of the development and deployment process:

1. **Main CI/CD Pipeline** (`ci-cd.yml`) - Complete build, test, and deploy
2. **Test Suite** (`test.yml`) - Comprehensive testing
3. **Dependency Updates** (`dependency-update.yml`) - Automated dependency management
4. **Manual Deployment** (`manual-deploy.yml`) - Manual deployment and rollback
5. **Release Management** (`release.yml`) - Version releases and documentation

## 📋 Workflow Details

### 1. Main CI/CD Pipeline (`ci-cd.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Tag pushes (e.g., `v1.0.0`)
- Pull requests to `main`

**Jobs:**
- **Test & Code Quality** - Unit tests, linting, type checking
- **Security Scan** - Vulnerability scanning with Trivy
- **Build & Push** - Docker image build and push to GCR
- **Deploy Staging** - Deploy to staging environment (develop branch)
- **Deploy Production** - Deploy to production (tag pushes)
- **Performance Test** - Load testing with Locust
- **Notify** - Slack/Discord notifications

### 2. Test Suite (`test.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests

**Jobs:**
- **Unit Tests** - Python 3.11 and 3.12 matrix testing
- **Integration Tests** - API integration testing
- **E2E Tests** - End-to-end testing
- **Performance Tests** - Load testing (main branch only)
- **Test Summary** - Aggregated test results

### 3. Dependency Updates (`dependency-update.yml`)

**Triggers:**
- Weekly schedule (Mondays at 9 AM UTC)
- Manual trigger

**Jobs:**
- **Dependency Update** - Update requirements files
- **Security Scan** - Python and Docker security scanning
- **Auto PR Creation** - Create PRs for dependency updates

### 4. Manual Deployment (`manual-deploy.yml`)

**Triggers:**
- Manual workflow dispatch

**Features:**
- Environment selection (staging/production)
- Image tag specification
- Force deployment option
- Automatic rollback on failure
- Health checks and smoke tests

### 5. Release Management (`release.yml`)

**Triggers:**
- Tag pushes (e.g., `v1.0.0`)
- Manual trigger

**Jobs:**
- **Create Release** - GitHub release creation
- **Update Documentation** - CHANGELOG and API docs
- **Notify Release** - Slack/Discord notifications

## 🏗️ Deployment Environments

### Staging Environment
- **Trigger:** Push to `develop` branch
- **URL:** `api-publishing-service-staging-xxx-uc.a.run.app`
- **Configuration:**
  - Memory: 1Gi
  - CPU: 1
  - Min instances: 0
  - Max instances: 5
  - Environment: staging

### Production Environment
- **Trigger:** Tag push (e.g., `v1.0.0`)
- **URL:** `api-publishing-service-xxx-uc.a.run.app`
- **Configuration:**
  - Memory: 2Gi
  - CPU: 2
  - Min instances: 1
  - Max instances: 20
  - Environment: production

## 🔧 Configuration

### Required Secrets

See [SECRETS.md](.github/SECRETS.md) for complete secret configuration.

**Essential Secrets:**
- `GCP_PROJECT_ID` - Google Cloud Project ID
- `GCP_SA_KEY` - Service Account JSON key

**Optional Secrets:**
- Platform API keys for testing
- Notification webhooks

### Environment Variables

The following environment variables are automatically configured:

```yaml
PROJECT_ID: ${{ secrets.GCP_PROJECT_ID }}
REGION: us-central1
SERVICE_NAME: api-publishing-service
REGISTRY: gcr.io
```

## 🚀 Deployment Process

### Automatic Deployment

1. **Development Flow:**
   ```bash
   git checkout develop
   git commit -m "feat: new feature"
   git push origin develop
   # → Triggers staging deployment
   ```

2. **Production Flow:**
   ```bash
   git checkout main
   git merge develop
   git tag v1.0.0
   git push origin main --tags
   # → Triggers production deployment
   ```

### Manual Deployment

1. Go to GitHub Actions tab
2. Select "Manual Deployment" workflow
3. Click "Run workflow"
4. Configure:
   - Environment (staging/production)
   - Image tag
   - Force deployment (optional)

### Rollback Process

1. **Automatic Rollback:**
   - Triggered on deployment failure
   - Rolls back to previous revision
   - Verifies rollback success

2. **Manual Rollback:**
   ```bash
   gcloud run services update-traffic api-publishing-service \
     --to-revisions=PREVIOUS_REVISION=100 \
     --region=us-central1
   ```

## 🧪 Testing Strategy

### Test Types

1. **Unit Tests** - Individual component testing
2. **Integration Tests** - API endpoint testing
3. **E2E Tests** - Complete workflow testing
4. **Performance Tests** - Load and stress testing
5. **Security Tests** - Vulnerability scanning

### Test Coverage

- **Minimum Coverage:** 80%
- **Target Coverage:** 90%
- **Coverage Reports:** Codecov integration

### Test Environments

- **Local Testing:** Docker Compose
- **CI Testing:** GitHub Actions with services
- **Staging Testing:** Cloud Run staging environment

## 📊 Monitoring and Observability

### Health Checks

- **Basic Health:** `/health`
- **Readiness:** `/health/ready`
- **Liveness:** `/health/live`

### Metrics

- **Prometheus Metrics:** `/metrics`
- **Custom Metrics:** Publishing success rates, response times
- **Platform Metrics:** Connection status, API response times

### Logging

- **Structured Logging:** JSON format
- **Request Tracing:** Unique request IDs
- **Error Tracking:** Comprehensive error logging

## 🔒 Security

### Security Scanning

1. **Code Scanning:** Trivy, Bandit, Safety
2. **Dependency Scanning:** Automated vulnerability checks
3. **Container Scanning:** Docker image security
4. **Secrets Scanning:** GitHub secret scanning

### Security Best Practices

1. **Least Privilege:** Minimal service account permissions
2. **Secret Management:** GitHub Secrets, Google Secret Manager
3. **Network Security:** VPC, firewall rules
4. **Container Security:** Non-root containers, minimal base images

## 📈 Performance Optimization

### Build Optimization

1. **Multi-stage Builds:** Separate build and runtime stages
2. **Layer Caching:** Optimized Docker layer caching
3. **Dependency Caching:** GitHub Actions cache
4. **Parallel Jobs:** Concurrent workflow execution

### Runtime Optimization

1. **Resource Limits:** Appropriate memory and CPU allocation
2. **Auto-scaling:** Cloud Run automatic scaling
3. **Connection Pooling:** Database and Redis connection pooling
4. **Caching:** Redis caching for improved performance

## 🛠️ Troubleshooting

### Common Issues

1. **Build Failures:**
   - Check Dockerfile syntax
   - Verify dependencies
   - Review build logs

2. **Deployment Failures:**
   - Verify Google Cloud permissions
   - Check service account configuration
   - Review Cloud Run logs

3. **Test Failures:**
   - Check test data configuration
   - Verify service dependencies
   - Review test logs

### Debug Commands

```bash
# Check workflow status
gh run list

# View workflow logs
gh run view RUN_ID

# Check Cloud Run status
gcloud run services list --region=us-central1

# View Cloud Run logs
gcloud logs read --service=api-publishing-service
```

## 📚 Best Practices

### Development

1. **Branch Strategy:** Feature branches → develop → main
2. **Commit Messages:** Conventional commits
3. **Code Review:** Required for main branch
4. **Testing:** Write tests for all new features

### Deployment

1. **Staging First:** Always test on staging
2. **Gradual Rollout:** Use traffic splitting for major releases
3. **Monitoring:** Watch metrics during deployment
4. **Rollback Plan:** Always have a rollback strategy

### Maintenance

1. **Regular Updates:** Keep dependencies updated
2. **Security Patches:** Apply security updates promptly
3. **Performance Monitoring:** Regular performance reviews
4. **Documentation:** Keep documentation updated

## 🆘 Support

For CI/CD pipeline issues:

1. **Check Workflow Logs:** GitHub Actions tab
2. **Review Documentation:** This guide and SECRETS.md
3. **Contact Support:** gratia@tin.info
4. **Create Issue:** GitHub Issues tab

## 📋 Checklist

### Before Deployment

- [ ] All tests passing
- [ ] Security scans clean
- [ ] Documentation updated
- [ ] Secrets configured
- [ ] Environment variables set

### After Deployment

- [ ] Health checks passing
- [ ] Metrics collection working
- [ ] Logs flowing correctly
- [ ] Performance within limits
- [ ] Notifications sent

This CI/CD pipeline provides a robust, automated deployment system that ensures code quality, security, and reliability for the API Publishing as a Service.
