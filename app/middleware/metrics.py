"""
Metrics middleware
"""

import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import structlog

logger = structlog.get_logger()

# Prometheus metrics
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

ACTIVE_REQUESTS = Counter(
    'http_active_requests',
    'Number of active HTTP requests'
)


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware for collecting metrics"""
    
    async def dispatch(self, request: Request, call_next):
        # Increment active requests
        ACTIVE_REQUESTS.inc()
        
        # Start time
        start_time = time.time()
        
        # Extract endpoint (remove query parameters and path parameters)
        endpoint = self._extract_endpoint(request.url.path)
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Record metrics
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=endpoint,
                status_code=response.status_code
            ).inc()
            
            REQUEST_DURATION.labels(
                method=request.method,
                endpoint=endpoint
            ).observe(duration)
            
            return response
        
        except Exception as e:
            # Calculate duration
            duration = time.time() - start_time
            
            # Record error metrics
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=endpoint,
                status_code=500
            ).inc()
            
            REQUEST_DURATION.labels(
                method=request.method,
                endpoint=endpoint
            ).observe(duration)
            
            raise
        
        finally:
            # Decrement active requests
            ACTIVE_REQUESTS.dec()
    
    def _extract_endpoint(self, path: str) -> str:
        """Extract endpoint from path for metrics"""
        # Remove common path parameters and normalize
        if path.startswith('/'):
            path = path[1:]
        
        # Replace common path parameters with placeholders
        path = path.replace('/health', '/health')
        path = path.replace('/platforms', '/platforms')
        path = path.replace('/content', '/content')
        
        # Remove trailing slashes
        path = path.rstrip('/')
        
        return path or 'root'
