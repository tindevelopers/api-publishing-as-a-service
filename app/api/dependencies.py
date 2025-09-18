"""
API dependencies
"""

from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import structlog

from app.services.publisher import ContentPublisher
from app.config import get_settings

logger = structlog.get_logger()
security = HTTPBearer(auto_error=False)


async def get_publisher() -> ContentPublisher:
    """Get content publisher service"""
    # In a real application, you might want to cache this
    return ContentPublisher()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
):
    """Get current authenticated user"""
    settings = get_settings()
    
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Simple token validation (in production, use proper JWT validation)
    if credentials.credentials != settings.secret_key:
        logger.warning("Invalid authentication token provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {"user_id": "api_user", "authenticated": True}


async def get_optional_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
):
    """Get optional authenticated user (for endpoints that work with or without auth)"""
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None
