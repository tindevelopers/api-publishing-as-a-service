"""
Locust performance test file for API Publishing as a Service
"""

from locust import HttpUser, task, between
import json


class APIUser(HttpUser):
    """Simulate API users for performance testing."""
    
    wait_time = between(1, 3)
    
    def on_start(self):
        """Set up test data when user starts."""
        self.headers = {
            "Authorization": "Bearer test-secret-key",
            "Content-Type": "application/json"
        }
        
        self.sample_content = {
            "type": "blog",
            "title": "Performance Test Blog Post",
            "content": "<h1>Performance Test</h1><p>This is a performance test blog post.</p>",
            "excerpt": "A performance test blog post",
            "tags": ["performance", "test"],
            "categories": ["testing"],
            "status": "draft",
            "seo": {
                "meta_title": "Performance Test Blog Post",
                "meta_description": "A performance test blog post",
                "keywords": ["performance", "test", "blog"]
            }
        }
    
    @task(3)
    def health_check(self):
        """Test health check endpoint (most frequent)."""
        self.client.get("/health")
    
    @task(2)
    def health_ready(self):
        """Test readiness check endpoint."""
        self.client.get("/health/ready")
    
    @task(2)
    def health_live(self):
        """Test liveness check endpoint."""
        self.client.get("/health/live")
    
    @task(1)
    def get_platforms(self):
        """Test getting available platforms."""
        self.client.get("/platforms", headers=self.headers)
    
    @task(1)
    def validate_content(self):
        """Test content validation endpoint."""
        self.client.post(
            "/content/validate",
            json=self.sample_content,
            headers=self.headers
        )
    
    @task(1)
    def validate_content_for_platform(self):
        """Test platform-specific content validation."""
        self.client.post(
            "/content/validate/webflow",
            json=self.sample_content,
            headers=self.headers
        )
    
    @task(1)
    def get_platform_status(self):
        """Test getting platform status."""
        self.client.get("/platforms/webflow/status", headers=self.headers)
    
    @task(1)
    def test_platform_connection(self):
        """Test platform connection."""
        self.client.post("/platforms/webflow/test", headers=self.headers)
    
    @task(1)
    def get_metrics(self):
        """Test metrics endpoint."""
        self.client.get("/metrics")
    
    @task(1)
    def get_api_docs(self):
        """Test API documentation endpoint."""
        self.client.get("/docs")
    
    @task(1)
    def get_root(self):
        """Test root endpoint."""
        self.client.get("/")


class PublishingUser(HttpUser):
    """Simulate users performing publishing operations."""
    
    wait_time = between(5, 10)  # Longer wait time for publishing operations
    
    def on_start(self):
        """Set up test data when user starts."""
        self.headers = {
            "Authorization": "Bearer test-secret-key",
            "Content-Type": "application/json"
        }
        
        self.publish_request = {
            "content": {
                "type": "blog",
                "title": "Performance Test Blog Post",
                "content": "<h1>Performance Test</h1><p>This is a performance test blog post.</p>",
                "excerpt": "A performance test blog post",
                "tags": ["performance", "test"],
                "categories": ["testing"],
                "status": "draft"
            },
            "platforms": ["webflow", "wordpress"],
            "options": {}
        }
    
    @task(1)
    def publish_content(self):
        """Test content publishing (less frequent due to complexity)."""
        self.client.post(
            "/content/publish",
            json=self.publish_request,
            headers=self.headers
        )
    
    @task(1)
    def batch_publish_content(self):
        """Test batch content publishing."""
        batch_request = {
            "content_items": [self.publish_request["content"]],
            "platforms": ["webflow"],
            "concurrency": 1
        }
        
        self.client.post(
            "/content/batch-publish",
            json=batch_request,
            headers=self.headers
        )
