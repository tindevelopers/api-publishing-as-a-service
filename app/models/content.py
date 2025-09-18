"""
Content models for AI Content Publisher API
Based on the TypeScript SDK structure
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field, validator, HttpUrl
import re


class ContentType(str, Enum):
    """Content type enumeration"""
    BLOG = "blog"
    FAQ = "faq"
    ARTICLE = "article"
    PRODUCT_DESCRIPTION = "product-description"
    LANDING_PAGE = "landing-page"


class ContentStatus(str, Enum):
    """Content status enumeration"""
    DRAFT = "draft"
    PUBLISHED = "published"
    SCHEDULED = "scheduled"


class PlatformType(str, Enum):
    """Platform type enumeration"""
    WEBFLOW = "webflow"
    WORDPRESS = "wordpress"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"


class ContentImage(BaseModel):
    """Image model for content"""
    url: HttpUrl
    alt_text: str = Field(..., description="Alt text for accessibility")
    caption: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None


class SEOConfig(BaseModel):
    """SEO configuration model"""
    meta_title: Optional[str] = Field(None, max_length=60, description="Meta title (max 60 chars)")
    meta_description: Optional[str] = Field(None, max_length=160, description="Meta description (max 160 chars)")
    keywords: Optional[List[str]] = Field(default_factory=list, description="SEO keywords")
    canonical_url: Optional[HttpUrl] = None
    og_title: Optional[str] = None
    og_description: Optional[str] = None
    og_image: Optional[HttpUrl] = None
    twitter_card: Optional[str] = "summary_large_image"
    twitter_site: Optional[str] = None

    @validator('meta_title')
    def validate_meta_title(cls, v):
        if v and len(v) > 60:
            raise ValueError('Meta title must be 60 characters or less')
        return v

    @validator('meta_description')
    def validate_meta_description(cls, v):
        if v and len(v) > 160:
            raise ValueError('Meta description must be 160 characters or less')
        return v


class FAQItem(BaseModel):
    """FAQ item model"""
    question: str = Field(..., min_length=1, max_length=500)
    answer: str = Field(..., min_length=1, max_length=2000)
    order: int = Field(..., ge=1, description="Display order")
    category: Optional[str] = None


class ProductSpecification(BaseModel):
    """Product specification model"""
    name: str = Field(..., min_length=1, max_length=100)
    value: str = Field(..., min_length=1, max_length=200)
    unit: Optional[str] = None
    category: Optional[str] = None


class AIContent(BaseModel):
    """Main AI Content model"""
    type: ContentType
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1, description="HTML content")
    excerpt: Optional[str] = Field(None, max_length=500)
    tags: Optional[List[str]] = Field(default_factory=list, max_items=20)
    categories: Optional[List[str]] = Field(default_factory=list, max_items=10)
    status: ContentStatus = ContentStatus.DRAFT
    seo: Optional[SEOConfig] = None
    images: Optional[List[ContentImage]] = Field(default_factory=list)
    publish_date: Optional[datetime] = None
    
    # Type-specific fields
    faqs: Optional[List[FAQItem]] = None
    specifications: Optional[List[ProductSpecification]] = None
    cta_text: Optional[str] = None
    cta_url: Optional[HttpUrl] = None
    
    # Metadata
    author: Optional[str] = None
    language: str = "en"
    featured_image: Optional[ContentImage] = None
    custom_fields: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @validator('title')
    def validate_title(cls, v):
        if not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()

    @validator('content')
    def validate_content(cls, v):
        if not v.strip():
            raise ValueError('Content cannot be empty')
        return v.strip()

    @validator('tags')
    def validate_tags(cls, v):
        if v:
            # Remove duplicates and empty strings
            v = list(set([tag.strip() for tag in v if tag.strip()]))
            if len(v) > 20:
                raise ValueError('Maximum 20 tags allowed')
        return v

    @validator('categories')
    def validate_categories(cls, v):
        if v:
            # Remove duplicates and empty strings
            v = list(set([cat.strip() for cat in v if cat.strip()]))
            if len(v) > 10:
                raise ValueError('Maximum 10 categories allowed')
        return v

    @validator('faqs')
    def validate_faqs(cls, v, values):
        if v and values.get('type') != ContentType.FAQ:
            raise ValueError('FAQs can only be set for FAQ content type')
        return v

    @validator('specifications')
    def validate_specifications(cls, v, values):
        if v and values.get('type') != ContentType.PRODUCT_DESCRIPTION:
            raise ValueError('Specifications can only be set for product description content type')
        return v


class PublishRequest(BaseModel):
    """Request model for publishing content"""
    content: AIContent
    platforms: List[PlatformType] = Field(..., min_items=1, description="Target platforms")
    options: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Platform-specific options")


class PublishResponse(BaseModel):
    """Response model for publishing content"""
    success: bool
    message: str
    content_id: Optional[str] = None
    url: Optional[HttpUrl] = None
    platform_results: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    errors: Optional[List[str]] = None
    warnings: Optional[List[str]] = None
    published_at: Optional[datetime] = None


class BatchPublishRequest(BaseModel):
    """Request model for batch publishing"""
    content_items: List[AIContent] = Field(..., min_items=1, max_items=100)
    platforms: List[PlatformType] = Field(..., min_items=1)
    options: Optional[Dict[str, Any]] = Field(default_factory=dict)
    concurrency: int = Field(default=3, ge=1, le=10, description="Concurrent publishing limit")
    stop_on_error: bool = Field(default=False, description="Stop batch on first error")


class BatchPublishResponse(BaseModel):
    """Response model for batch publishing"""
    success: bool
    total_items: int
    successful_items: int
    failed_items: int
    results: List[PublishResponse] = Field(default_factory=list)
    errors: Optional[List[str]] = None
    completed_at: Optional[datetime] = None


class ContentValidationResult(BaseModel):
    """Content validation result model"""
    is_valid: bool
    errors: List[Dict[str, str]] = Field(default_factory=list)
    warnings: List[Dict[str, str]] = Field(default_factory=list)
    score: int = Field(..., ge=0, le=100, description="Validation score out of 100")


class PlatformConfig(BaseModel):
    """Platform configuration model"""
    platform: PlatformType
    enabled: bool = True
    credentials: Dict[str, str] = Field(..., description="Platform-specific credentials")
    settings: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ScheduleConfig(BaseModel):
    """Content scheduling configuration"""
    platforms: List[PlatformType] = Field(..., min_items=1)
    frequency: Dict[str, Any] = Field(..., description="Scheduling frequency")
    timezone: str = Field(default="UTC", description="Timezone for scheduling")
    auto_test: bool = Field(default=True, description="Auto-test content before publishing")
    retry_failed: bool = Field(default=True, description="Retry failed publishes")


class ScheduledContent(BaseModel):
    """Scheduled content model"""
    id: str
    content: AIContent
    platforms: List[PlatformType]
    scheduled_for: datetime
    priority: str = Field(default="normal", regex="^(low|normal|high|urgent)$")
    status: str = Field(default="pending", regex="^(pending|processing|completed|failed|cancelled)$")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
