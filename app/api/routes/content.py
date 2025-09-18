"""
Content publishing endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from app.models.content import (
    AIContent, PublishRequest, PublishResponse, BatchPublishRequest, 
    BatchPublishResponse, ContentValidationResult
)
from app.services.publisher import ContentPublisher
from app.api.dependencies import get_publisher, get_current_user, get_optional_user
import structlog

logger = structlog.get_logger()
router = APIRouter()


@router.post("/validate", response_model=ContentValidationResult)
async def validate_content(
    content: AIContent,
    publisher: ContentPublisher = Depends(get_publisher),
    current_user: dict = Depends(get_optional_user)
):
    """Validate content before publishing"""
    try:
        validation_result = await publisher.validate_content(content)
        
        logger.info(
            "Content validation completed",
            is_valid=validation_result.is_valid,
            score=validation_result.score,
            error_count=len(validation_result.errors),
            warning_count=len(validation_result.warnings)
        )
        
        return validation_result
    
    except Exception as e:
        logger.error("Content validation failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Content validation failed: {str(e)}"
        )


@router.post("/validate/{platform}", response_model=ContentValidationResult)
async def validate_content_for_platform(
    platform: str,
    content: AIContent,
    publisher: ContentPublisher = Depends(get_publisher),
    current_user: dict = Depends(get_optional_user)
):
    """Validate content for a specific platform"""
    try:
        validation_result = await publisher.validate_content_for_platform(content, platform)
        
        logger.info(
            "Platform-specific content validation completed",
            platform=platform,
            is_valid=validation_result.is_valid,
            score=validation_result.score,
            error_count=len(validation_result.errors),
            warning_count=len(validation_result.warnings)
        )
        
        return validation_result
    
    except Exception as e:
        logger.error("Platform-specific content validation failed", platform=platform, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Platform-specific content validation failed: {str(e)}"
        )


@router.post("/publish", response_model=PublishResponse)
async def publish_content(
    request: PublishRequest,
    background_tasks: BackgroundTasks,
    publisher: ContentPublisher = Depends(get_publisher),
    current_user: dict = Depends(get_current_user)
):
    """Publish content to specified platforms"""
    try:
        logger.info(
            "Content publishing started",
            content_type=request.content.type,
            platforms=request.platforms,
            user_id=current_user.get("user_id")
        )
        
        result = await publisher.publish(request)
        
        # Log the result
        if result.success:
            logger.info(
                "Content published successfully",
                content_id=result.content_id,
                platforms=request.platforms,
                url=result.url
            )
        else:
            logger.warning(
                "Content publishing failed",
                platforms=request.platforms,
                errors=result.errors
            )
        
        return result
    
    except Exception as e:
        logger.error("Content publishing failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Content publishing failed: {str(e)}"
        )


@router.post("/batch-publish", response_model=BatchPublishResponse)
async def batch_publish_content(
    request: BatchPublishRequest,
    background_tasks: BackgroundTasks,
    publisher: ContentPublisher = Depends(get_publisher),
    current_user: dict = Depends(get_current_user)
):
    """Publish multiple content items"""
    try:
        logger.info(
            "Batch content publishing started",
            total_items=len(request.content_items),
            platforms=request.platforms,
            concurrency=request.concurrency,
            user_id=current_user.get("user_id")
        )
        
        result = await publisher.batch_publish(request)
        
        # Log the result
        logger.info(
            "Batch content publishing completed",
            total_items=result.total_items,
            successful_items=result.successful_items,
            failed_items=result.failed_items,
            success=result.success
        )
        
        return result
    
    except Exception as e:
        logger.error("Batch content publishing failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch content publishing failed: {str(e)}"
        )


@router.get("/platforms")
async def get_available_platforms(
    publisher: ContentPublisher = Depends(get_publisher),
    current_user: dict = Depends(get_optional_user)
):
    """Get list of available platforms for publishing"""
    try:
        platforms = publisher.get_available_platforms()
        platform_status = publisher.get_platform_status()
        
        return {
            "available_platforms": platforms,
            "platform_status": platform_status,
            "total_platforms": len(platforms)
        }
    
    except Exception as e:
        logger.error("Failed to get available platforms", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get available platforms: {str(e)}"
        )
