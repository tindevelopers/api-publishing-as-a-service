"""
Main content publisher service
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from app.models.content import (
    AIContent, PublishRequest, PublishResponse, BatchPublishRequest, 
    BatchPublishResponse, PlatformType, ContentValidationResult
)
from app.services.validation import ContentValidator
from app.services.platforms.webflow import WebflowService
from app.services.platforms.wordpress import WordPressService
from app.config import get_settings, get_platform_config, is_platform_enabled


class ContentPublisher:
    """Main content publisher service"""
    
    def __init__(self):
        self.settings = get_settings()
        self.validator = ContentValidator()
        self.platforms = self._initialize_platforms()
    
    def _initialize_platforms(self) -> Dict[str, Any]:
        """Initialize platform services"""
        platforms = {}
        
        # Initialize Webflow
        if is_platform_enabled("webflow"):
            webflow_config = get_platform_config("webflow")
            platforms["webflow"] = WebflowService(webflow_config)
        
        # Initialize WordPress
        if is_platform_enabled("wordpress"):
            wordpress_config = get_platform_config("wordpress")
            platforms["wordpress"] = WordPressService(wordpress_config)
        
        # TODO: Add LinkedIn and Twitter services
        # if is_platform_enabled("linkedin"):
        #     linkedin_config = get_platform_config("linkedin")
        #     platforms["linkedin"] = LinkedInService(linkedin_config)
        
        # if is_platform_enabled("twitter"):
        #     twitter_config = get_platform_config("twitter")
        #     platforms["twitter"] = TwitterService(twitter_config)
        
        return platforms
    
    async def publish(self, request: PublishRequest) -> PublishResponse:
        """Publish content to specified platforms"""
        try:
            # Validate content first
            validation_result = self.validator.validate_content(request.content)
            if not validation_result.is_valid:
                return PublishResponse(
                    success=False,
                    message="Content validation failed",
                    errors=[error["message"] for error in validation_result.errors],
                    warnings=[warning["message"] for warning in validation_result.warnings]
                )
            
            # Check if all requested platforms are available
            unavailable_platforms = []
            for platform in request.platforms:
                if platform.value not in self.platforms:
                    unavailable_platforms.append(platform.value)
            
            if unavailable_platforms:
                return PublishResponse(
                    success=False,
                    message=f"Platforms not available: {', '.join(unavailable_platforms)}",
                    errors=[f"Platform {platform} is not configured or enabled" for platform in unavailable_platforms]
                )
            
            # Publish to each platform
            platform_results = {}
            all_successful = True
            errors = []
            warnings = []
            
            for platform in request.platforms:
                platform_name = platform.value
                platform_service = self.platforms[platform_name]
                
                try:
                    # Validate content for specific platform
                    platform_validation = self.validator.validate_for_platform(request.content, platform_name)
                    if not platform_validation.is_valid:
                        platform_results[platform_name] = {
                            "success": False,
                            "message": "Platform-specific validation failed",
                            "errors": [error["message"] for error in platform_validation.errors]
                        }
                        all_successful = False
                        continue
                    
                    # Publish to platform
                    result = await platform_service.publish(request.content, request.options)
                    platform_results[platform_name] = {
                        "success": result.success,
                        "message": result.message,
                        "content_id": result.content_id,
                        "url": str(result.url) if result.url else None,
                        "errors": result.errors or [],
                        "warnings": result.warnings or []
                    }
                    
                    if not result.success:
                        all_successful = False
                        errors.extend(result.errors or [])
                    else:
                        warnings.extend(result.warnings or [])
                
                except Exception as e:
                    platform_results[platform_name] = {
                        "success": False,
                        "message": f"Error publishing to {platform_name}: {str(e)}",
                        "errors": [str(e)]
                    }
                    all_successful = False
                    errors.append(f"Error publishing to {platform_name}: {str(e)}")
            
            # Determine overall success
            if all_successful:
                message = f"Content published successfully to {len(request.platforms)} platform(s)"
                # Get the first successful result for main response
                first_successful = next(
                    (result for result in platform_results.values() if result["success"]), 
                    None
                )
                content_id = first_successful["content_id"] if first_successful else None
                url = first_successful["url"] if first_successful else None
            else:
                message = "Content publishing completed with some failures"
                content_id = None
                url = None
            
            return PublishResponse(
                success=all_successful,
                message=message,
                content_id=content_id,
                url=url,
                platform_results=platform_results,
                errors=errors if errors else None,
                warnings=warnings if warnings else None,
                published_at=datetime.utcnow()
            )
        
        except Exception as e:
            return PublishResponse(
                success=False,
                message=f"Unexpected error during publishing: {str(e)}",
                errors=[str(e)]
            )
    
    async def batch_publish(self, request: BatchPublishRequest) -> BatchPublishResponse:
        """Publish multiple content items"""
        try:
            # Validate batch size
            if len(request.content_items) > self.settings.max_batch_size:
                return BatchPublishResponse(
                    success=False,
                    total_items=len(request.content_items),
                    successful_items=0,
                    failed_items=len(request.content_items),
                    errors=[f"Batch size exceeds maximum of {self.settings.max_batch_size} items"]
                )
            
            # Create semaphore for concurrency control
            semaphore = asyncio.Semaphore(request.concurrency)
            
            async def publish_single_item(content: AIContent) -> PublishResponse:
                async with semaphore:
                    publish_request = PublishRequest(
                        content=content,
                        platforms=request.platforms,
                        options=request.options
                    )
                    return await self.publish(publish_request)
            
            # Publish all items concurrently
            tasks = [publish_single_item(content) for content in request.content_items]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            successful_items = 0
            failed_items = 0
            processed_results = []
            errors = []
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    processed_results.append(PublishResponse(
                        success=False,
                        message=f"Error processing item {i+1}: {str(result)}",
                        errors=[str(result)]
                    ))
                    failed_items += 1
                    if request.stop_on_error:
                        errors.append(f"Stopped at item {i+1} due to error: {str(result)}")
                        break
                else:
                    processed_results.append(result)
                    if result.success:
                        successful_items += 1
                    else:
                        failed_items += 1
                        if request.stop_on_error:
                            errors.append(f"Stopped at item {i+1} due to publishing failure")
                            break
            
            return BatchPublishResponse(
                success=failed_items == 0,
                total_items=len(request.content_items),
                successful_items=successful_items,
                failed_items=failed_items,
                results=processed_results,
                errors=errors if errors else None,
                completed_at=datetime.utcnow()
            )
        
        except Exception as e:
            return BatchPublishResponse(
                success=False,
                total_items=len(request.content_items),
                successful_items=0,
                failed_items=len(request.content_items),
                errors=[f"Unexpected error during batch publishing: {str(e)}"]
            )
    
    async def validate_content(self, content: AIContent) -> ContentValidationResult:
        """Validate content"""
        return self.validator.validate_content(content)
    
    async def validate_content_for_platform(self, content: AIContent, platform: str) -> ContentValidationResult:
        """Validate content for specific platform"""
        return self.validator.validate_for_platform(content, platform)
    
    async def test_platform_connections(self) -> Dict[str, bool]:
        """Test connections to all configured platforms"""
        results = {}
        
        for platform_name, platform_service in self.platforms.items():
            try:
                results[platform_name] = await platform_service.test_connection()
            except Exception:
                results[platform_name] = False
        
        return results
    
    def get_available_platforms(self) -> List[str]:
        """Get list of available platforms"""
        return list(self.platforms.keys())
    
    def get_platform_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all platforms"""
        status = {}
        
        for platform_name, platform_service in self.platforms.items():
            status[platform_name] = {
                "enabled": True,
                "configured": platform_service.validate_config(),
                "name": platform_service.get_platform_name()
            }
        
        return status
