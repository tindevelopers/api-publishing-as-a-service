"""
Health check endpoints
"""

from fastapi import APIRouter, Depends
from app.services.publisher import ContentPublisher
from app.api.dependencies import get_publisher
import structlog

logger = structlog.get_logger()
router = APIRouter()


@router.get("/")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "service": "AI Content Publisher API",
        "version": "1.0.0"
    }


@router.get("/ready")
async def readiness_check(publisher: ContentPublisher = Depends(get_publisher)):
    """Readiness check - verifies all dependencies are available"""
    try:
        # Test platform connections
        platform_status = await publisher.test_platform_connections()
        
        # Check if at least one platform is available
        available_platforms = [name for name, status in platform_status.items() if status]
        
        if not available_platforms:
            return {
                "status": "not_ready",
                "message": "No platforms are available",
                "platforms": platform_status
            }
        
        return {
            "status": "ready",
            "message": f"Service ready with {len(available_platforms)} platform(s)",
            "platforms": platform_status,
            "available_platforms": available_platforms
        }
    
    except Exception as e:
        logger.error("Readiness check failed", error=str(e))
        return {
            "status": "not_ready",
            "message": f"Readiness check failed: {str(e)}"
        }


@router.get("/live")
async def liveness_check():
    """Liveness check - verifies the service is running"""
    return {
        "status": "alive",
        "timestamp": "2024-01-01T00:00:00Z"  # In production, use actual timestamp
    }
