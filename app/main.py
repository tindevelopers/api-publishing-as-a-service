"""
AI Content Publisher API - Main FastAPI application
"""

import logging
import time
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import structlog

from app.config import get_settings
from app.models.content import (
    AIContent, PublishRequest, PublishResponse, BatchPublishRequest, 
    BatchPublishResponse, ContentValidationResult, PlatformType
)
from app.services.publisher import ContentPublisher
from app.api.dependencies import get_publisher, get_current_user
from app.api.routes import content, health, platforms
from app.middleware.logging import LoggingMiddleware
from app.middleware.metrics import MetricsMiddleware


# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting AI Content Publisher API", version=app.version)
    
    # Initialize publisher
    publisher = ContentPublisher()
    app.state.publisher = publisher
    
    # Test platform connections
    platform_status = await publisher.test_platform_connections()
    logger.info("Platform connections tested", status=platform_status)
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Content Publisher API")


# Create FastAPI application
app = FastAPI(
    title="AI Content Publisher API",
    description="API for publishing AI-generated content to multiple platforms",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Get settings
settings = get_settings()

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=settings.allowed_methods,
    allow_headers=settings.allowed_headers,
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if settings.debug else ["localhost", "127.0.0.1"]
)

app.add_middleware(LoggingMiddleware)
app.add_middleware(MetricsMiddleware)

# Include routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(platforms.router, prefix="/platforms", tags=["platforms"])
app.include_router(content.router, prefix="/content", tags=["content"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Content Publisher API",
        "version": app.version,
        "docs": "/docs",
        "health": "/health"
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    logger.error(
        "HTTP exception occurred",
        status_code=exc.status_code,
        detail=exc.detail,
        path=request.url.path
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code,
            "path": request.url.path
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    logger.error(
        "Unhandled exception occurred",
        error=str(exc),
        path=request.url.path,
        exc_info=True
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Internal server error",
            "status_code": 500,
            "path": request.url.path
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        workers=1 if settings.debug else settings.workers,
        log_level=settings.log_level.lower()
    )
