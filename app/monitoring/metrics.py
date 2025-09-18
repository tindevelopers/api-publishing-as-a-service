"""
Metrics collection and Prometheus integration
"""

from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
import time
from typing import Dict, Any


# Content publishing metrics
CONTENT_PUBLISHED_TOTAL = Counter(
    'content_published_total',
    'Total number of content items published',
    ['platform', 'content_type', 'status']
)

CONTENT_PUBLISH_DURATION = Histogram(
    'content_publish_duration_seconds',
    'Time spent publishing content',
    ['platform', 'content_type']
)

CONTENT_VALIDATION_TOTAL = Counter(
    'content_validation_total',
    'Total number of content validations',
    ['status', 'platform']
)

CONTENT_VALIDATION_SCORE = Histogram(
    'content_validation_score',
    'Content validation scores',
    ['platform']
)

# Platform metrics
PLATFORM_CONNECTION_TESTS = Counter(
    'platform_connection_tests_total',
    'Total number of platform connection tests',
    ['platform', 'status']
)

PLATFORM_RESPONSE_TIME = Histogram(
    'platform_response_time_seconds',
    'Platform API response time',
    ['platform', 'endpoint']
)

# Batch processing metrics
BATCH_PUBLISH_TOTAL = Counter(
    'batch_publish_total',
    'Total number of batch publish operations',
    ['status']
)

BATCH_PUBLISH_SIZE = Histogram(
    'batch_publish_size',
    'Number of items in batch publish operations'
)

BATCH_PUBLISH_DURATION = Histogram(
    'batch_publish_duration_seconds',
    'Time spent on batch publish operations'
)

# System metrics
ACTIVE_REQUESTS = Gauge(
    'active_requests',
    'Number of active HTTP requests'
)

REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)


class MetricsCollector:
    """Metrics collection utility"""
    
    @staticmethod
    def record_content_published(platform: str, content_type: str, success: bool):
        """Record content publishing metric"""
        status = 'success' if success else 'failure'
        CONTENT_PUBLISHED_TOTAL.labels(
            platform=platform,
            content_type=content_type,
            status=status
        ).inc()
    
    @staticmethod
    def record_content_publish_duration(platform: str, content_type: str, duration: float):
        """Record content publishing duration"""
        CONTENT_PUBLISH_DURATION.labels(
            platform=platform,
            content_type=content_type
        ).observe(duration)
    
    @staticmethod
    def record_content_validation(platform: str, success: bool, score: int):
        """Record content validation metric"""
        status = 'success' if success else 'failure'
        CONTENT_VALIDATION_TOTAL.labels(
            platform=platform,
            status=status
        ).inc()
        
        CONTENT_VALIDATION_SCORE.labels(
            platform=platform
        ).observe(score)
    
    @staticmethod
    def record_platform_connection_test(platform: str, success: bool):
        """Record platform connection test"""
        status = 'success' if success else 'failure'
        PLATFORM_CONNECTION_TESTS.labels(
            platform=platform,
            status=status
        ).inc()
    
    @staticmethod
    def record_platform_response_time(platform: str, endpoint: str, duration: float):
        """Record platform response time"""
        PLATFORM_RESPONSE_TIME.labels(
            platform=platform,
            endpoint=endpoint
        ).observe(duration)
    
    @staticmethod
    def record_batch_publish(success: bool, size: int, duration: float):
        """Record batch publish metrics"""
        status = 'success' if success else 'failure'
        BATCH_PUBLISH_TOTAL.labels(status=status).inc()
        BATCH_PUBLISH_SIZE.observe(size)
        BATCH_PUBLISH_DURATION.observe(duration)
    
    @staticmethod
    def record_http_request(method: str, endpoint: str, status_code: int, duration: float):
        """Record HTTP request metrics"""
        REQUEST_COUNT.labels(
            method=method,
            endpoint=endpoint,
            status_code=status_code
        ).inc()
        
        REQUEST_DURATION.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
    
    @staticmethod
    def set_active_requests(count: int):
        """Set active requests count"""
        ACTIVE_REQUESTS.set(count)


def get_metrics_response() -> Response:
    """Get Prometheus metrics response"""
    metrics_data = generate_latest()
    return Response(
        content=metrics_data,
        media_type=CONTENT_TYPE_LATEST
    )


class MetricsTimer:
    """Context manager for timing operations"""
    
    def __init__(self, collector: MetricsCollector, platform: str = None, content_type: str = None, endpoint: str = None):
        self.collector = collector
        self.platform = platform
        self.content_type = content_type
        self.endpoint = endpoint
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = time.time() - self.start_time
            
            if self.platform and self.content_type:
                self.collector.record_content_publish_duration(self.platform, self.content_type, duration)
            elif self.platform and self.endpoint:
                self.collector.record_platform_response_time(self.platform, self.endpoint, duration)
