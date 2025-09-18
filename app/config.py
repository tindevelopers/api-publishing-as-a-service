"""
Configuration settings for AI Content Publisher API
"""

import os
from typing import Dict, List, Optional, Any
from pydantic import BaseSettings, Field, validator
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    app_name: str = "AI Content Publisher API"
    app_version: str = "1.0.0"
    debug: bool = Field(default=False, env="DEBUG")
    environment: str = Field(default="production", env="ENVIRONMENT")
    
    # Server
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8080, env="PORT")
    workers: int = Field(default=1, env="WORKERS")
    
    # Security
    secret_key: str = Field(..., env="SECRET_KEY")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    
    # CORS
    allowed_origins: List[str] = Field(
        default=["*"], 
        env="ALLOWED_ORIGINS"
    )
    allowed_methods: List[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        env="ALLOWED_METHODS"
    )
    allowed_headers: List[str] = Field(
        default=["*"],
        env="ALLOWED_HEADERS"
    )
    
    # Database
    database_url: str = Field(..., env="DATABASE_URL")
    database_pool_size: int = Field(default=10, env="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=20, env="DATABASE_MAX_OVERFLOW")
    
    # Redis
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    redis_password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    redis_db: int = Field(default=0, env="REDIS_DB")
    
    # Celery
    celery_broker_url: str = Field(default="redis://localhost:6379/1", env="CELERY_BROKER_URL")
    celery_result_backend: str = Field(default="redis://localhost:6379/2", env="CELERY_RESULT_BACKEND")
    
    # Platform Configurations
    webflow_api_key: Optional[str] = Field(default=None, env="WEBFLOW_API_KEY")
    webflow_site_id: Optional[str] = Field(default=None, env="WEBFLOW_SITE_ID")
    webflow_collection_id: Optional[str] = Field(default=None, env="WEBFLOW_COLLECTION_ID")
    
    wordpress_site_url: Optional[str] = Field(default=None, env="WORDPRESS_SITE_URL")
    wordpress_username: Optional[str] = Field(default=None, env="WORDPRESS_USERNAME")
    wordpress_password: Optional[str] = Field(default=None, env="WORDPRESS_PASSWORD")
    wordpress_app_password: Optional[str] = Field(default=None, env="WORDPRESS_APP_PASSWORD")
    
    linkedin_access_token: Optional[str] = Field(default=None, env="LINKEDIN_ACCESS_TOKEN")
    linkedin_user_id: Optional[str] = Field(default=None, env="LINKEDIN_USER_ID")
    
    twitter_api_key: Optional[str] = Field(default=None, env="TWITTER_API_KEY")
    twitter_api_secret: Optional[str] = Field(default=None, env="TWITTER_API_SECRET")
    twitter_access_token: Optional[str] = Field(default=None, env="TWITTER_ACCESS_TOKEN")
    twitter_access_token_secret: Optional[str] = Field(default=None, env="TWITTER_ACCESS_TOKEN_SECRET")
    
    # Rate Limiting
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=3600, env="RATE_LIMIT_WINDOW")  # 1 hour
    
    # Content Processing
    max_content_length: int = Field(default=100000, env="MAX_CONTENT_LENGTH")  # 100KB
    max_images_per_content: int = Field(default=20, env="MAX_IMAGES_PER_CONTENT")
    allowed_image_types: List[str] = Field(
        default=["image/jpeg", "image/png", "image/gif", "image/webp"],
        env="ALLOWED_IMAGE_TYPES"
    )
    
    # Publishing
    default_timeout: int = Field(default=30, env="DEFAULT_TIMEOUT")
    max_retries: int = Field(default=3, env="MAX_RETRIES")
    retry_delay: int = Field(default=1, env="RETRY_DELAY")  # seconds
    
    # Batch Processing
    max_batch_size: int = Field(default=100, env="MAX_BATCH_SIZE")
    batch_concurrency: int = Field(default=3, env="BATCH_CONCURRENCY")
    
    # Monitoring & Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    enable_tracing: bool = Field(default=True, env="ENABLE_TRACING")
    
    # Google Cloud
    google_cloud_project: Optional[str] = Field(default=None, env="GOOGLE_CLOUD_PROJECT")
    google_cloud_region: str = Field(default="us-central1", env="GOOGLE_CLOUD_REGION")
    
    # Health Check
    health_check_interval: int = Field(default=30, env="HEALTH_CHECK_INTERVAL")
    
    @validator('allowed_origins', pre=True)
    def parse_allowed_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    @validator('allowed_methods', pre=True)
    def parse_allowed_methods(cls, v):
        if isinstance(v, str):
            return [method.strip() for method in v.split(',')]
        return v
    
    @validator('allowed_headers', pre=True)
    def parse_allowed_headers(cls, v):
        if isinstance(v, str):
            return [header.strip() for header in v.split(',')]
        return v
    
    @validator('allowed_image_types', pre=True)
    def parse_allowed_image_types(cls, v):
        if isinstance(v, str):
            return [img_type.strip() for img_type in v.split(',')]
        return v
    
    @validator('environment')
    def validate_environment(cls, v):
        allowed_envs = ['development', 'staging', 'production']
        if v not in allowed_envs:
            raise ValueError(f'Environment must be one of: {allowed_envs}')
        return v
    
    @validator('log_level')
    def validate_log_level(cls, v):
        allowed_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in allowed_levels:
            raise ValueError(f'Log level must be one of: {allowed_levels}')
        return v.upper()
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Platform-specific configuration helpers
def get_platform_config(platform: str) -> Dict[str, Any]:
    """Get platform-specific configuration"""
    settings = get_settings()
    
    configs = {
        "webflow": {
            "api_key": settings.webflow_api_key,
            "site_id": settings.webflow_site_id,
            "collection_id": settings.webflow_collection_id,
        },
        "wordpress": {
            "site_url": settings.wordpress_site_url,
            "username": settings.wordpress_username,
            "password": settings.wordpress_password,
            "app_password": settings.wordpress_app_password,
        },
        "linkedin": {
            "access_token": settings.linkedin_access_token,
            "user_id": settings.linkedin_user_id,
        },
        "twitter": {
            "api_key": settings.twitter_api_key,
            "api_secret": settings.twitter_api_secret,
            "access_token": settings.twitter_access_token,
            "access_token_secret": settings.twitter_access_token_secret,
        }
    }
    
    return configs.get(platform, {})


def is_platform_enabled(platform: str) -> bool:
    """Check if platform is enabled and configured"""
    config = get_platform_config(platform)
    return all(value is not None for value in config.values())


def get_enabled_platforms() -> List[str]:
    """Get list of enabled platforms"""
    platforms = ["webflow", "wordpress", "linkedin", "twitter"]
    return [platform for platform in platforms if is_platform_enabled(platform)]
