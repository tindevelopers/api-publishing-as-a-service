"""
Platform management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from app.services.publisher import ContentPublisher
from app.api.dependencies import get_publisher, get_current_user
import structlog

logger = structlog.get_logger()
router = APIRouter()


@router.get("/")
async def list_platforms(
    publisher: ContentPublisher = Depends(get_publisher),
    current_user: dict = Depends(get_current_user)
):
    """List all available platforms and their status"""
    try:
        platform_status = publisher.get_platform_status()
        available_platforms = publisher.get_available_platforms()
        
        return {
            "platforms": platform_status,
            "available_platforms": available_platforms,
            "total_platforms": len(available_platforms)
        }
    
    except Exception as e:
        logger.error("Failed to list platforms", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list platforms: {str(e)}"
        )


@router.get("/{platform_name}/status")
async def get_platform_status(
    platform_name: str,
    publisher: ContentPublisher = Depends(get_publisher),
    current_user: dict = Depends(get_current_user)
):
    """Get status of a specific platform"""
    try:
        platform_status = publisher.get_platform_status()
        
        if platform_name not in platform_status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Platform '{platform_name}' not found"
            )
        
        # Test connection
        connection_status = await publisher.test_platform_connections()
        
        return {
            "platform": platform_name,
            "status": platform_status[platform_name],
            "connection": connection_status.get(platform_name, False)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get platform status", platform=platform_name, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get platform status: {str(e)}"
        )


@router.post("/{platform_name}/test")
async def test_platform_connection(
    platform_name: str,
    publisher: ContentPublisher = Depends(get_publisher),
    current_user: dict = Depends(get_current_user)
):
    """Test connection to a specific platform"""
    try:
        platform_status = publisher.get_platform_status()
        
        if platform_name not in platform_status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Platform '{platform_name}' not found"
            )
        
        # Test connection
        connection_status = await publisher.test_platform_connections()
        is_connected = connection_status.get(platform_name, False)
        
        return {
            "platform": platform_name,
            "connected": is_connected,
            "message": "Connection successful" if is_connected else "Connection failed"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to test platform connection", platform=platform_name, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to test platform connection: {str(e)}"
        )


@router.post("/test-all")
async def test_all_platform_connections(
    publisher: ContentPublisher = Depends(get_publisher),
    current_user: dict = Depends(get_current_user)
):
    """Test connections to all platforms"""
    try:
        connection_status = await publisher.test_platform_connections()
        
        successful_connections = [name for name, status in connection_status.items() if status]
        failed_connections = [name for name, status in connection_status.items() if not status]
        
        return {
            "connections": connection_status,
            "successful": successful_connections,
            "failed": failed_connections,
            "total_platforms": len(connection_status),
            "successful_count": len(successful_connections),
            "failed_count": len(failed_connections)
        }
    
    except Exception as e:
        logger.error("Failed to test all platform connections", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to test platform connections: {str(e)}"
        )
