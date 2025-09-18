# GitHub Actions Secrets Configuration

This document outlines the required secrets for the GitHub Actions CI/CD workflows.

## Required Secrets

### Google Cloud Platform
- **`GCP_PROJECT_ID`** - Your Google Cloud Project ID
- **`GCP_SA_KEY`** - Service Account JSON key for authentication

### Platform API Keys (Optional - for testing)
- **`WEBFLOW_API_KEY`** - Webflow API key for testing
- **`WEBFLOW_SITE_ID`** - Webflow site ID for testing
- **`WORDPRESS_SITE_URL`** - WordPress site URL for testing
- **`WORDPRESS_APP_PASSWORD`** - WordPress app password for testing
- **`LINKEDIN_ACCESS_TOKEN`** - LinkedIn access token for testing
- **`TWITTER_API_KEY`** - Twitter API key for testing
- **`TWITTER_API_SECRET`** - Twitter API secret for testing

### Notification (Optional)
- **`SLACK_WEBHOOK`** - Slack webhook URL for notifications
- **`DISCORD_WEBHOOK`** - Discord webhook URL for notifications

## Setting Up Secrets

### 1. Google Cloud Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to IAM & Admin > Service Accounts
3. Create a new service account or use existing one
4. Grant the following roles:
   - Cloud Run Admin
   - Storage Admin
   - Cloud Build Editor
   - Service Account User
5. Create a JSON key and download it
6. Add the JSON content as `GCP_SA_KEY` secret

### 2. GitHub Secrets Setup

1. Go to your GitHub repository
2. Navigate to Settings > Secrets and variables > Actions
3. Click "New repository secret"
4. Add each secret with the exact name listed above

## Environment Variables

The following environment variables are automatically set in the workflows:

- `PROJECT_ID` - From `GCP_PROJECT_ID` secret
- `REGION` - Set to `us-central1`
- `SERVICE_NAME` - Set to `api-publishing-service`
- `REGISTRY` - Set to `gcr.io`

## Security Best Practices

1. **Rotate secrets regularly** - Update API keys and service account keys periodically
2. **Use least privilege** - Only grant necessary permissions to service accounts
3. **Monitor usage** - Regularly check Google Cloud Console for unexpected usage
4. **Secure storage** - Never commit secrets to the repository
5. **Environment separation** - Use different secrets for staging and production

## Troubleshooting

### Common Issues

1. **Authentication failures**
   - Verify `GCP_SA_KEY` is valid JSON
   - Check service account has required permissions
   - Ensure project ID is correct

2. **Deployment failures**
   - Check Cloud Run API is enabled
   - Verify container registry permissions
   - Ensure service account can deploy to Cloud Run

3. **Test failures**
   - Verify platform API keys are valid
   - Check network connectivity
   - Ensure test data is properly configured

### Debug Commands

```bash
# Test Google Cloud authentication
gcloud auth list

# Test service account permissions
gcloud projects get-iam-policy YOUR_PROJECT_ID

# Test Cloud Run access
gcloud run services list --region=us-central1
```

## Cost Optimization

1. **Use staging environment** - Test deployments on staging first
2. **Monitor resource usage** - Set up billing alerts
3. **Optimize container size** - Use multi-stage builds
4. **Set appropriate limits** - Configure min/max instances
5. **Clean up resources** - Remove unused images and services

## Support

For issues with the CI/CD pipeline:
1. Check the Actions tab in GitHub
2. Review workflow logs for specific errors
3. Verify all secrets are properly configured
4. Contact: gratia@tin.info
