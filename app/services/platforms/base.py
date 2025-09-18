"""
Base platform service
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from app.models.content import AIContent, PublishResponse


class BasePlatformService(ABC):
    """Base class for platform publishing services"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = self.__class__.__name__.replace('Service', '').lower()
    
    @abstractmethod
    async def publish(self, content: AIContent, options: Optional[Dict[str, Any]] = None) -> PublishResponse:
        """Publish content to the platform"""
        pass
    
    @abstractmethod
    async def test_connection(self) -> bool:
        """Test platform connection"""
        pass
    
    @abstractmethod
    async def get_content(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Get published content by ID"""
        pass
    
    @abstractmethod
    async def update_content(self, content_id: str, content: AIContent, options: Optional[Dict[str, Any]] = None) -> PublishResponse:
        """Update published content"""
        pass
    
    @abstractmethod
    async def delete_content(self, content_id: str) -> bool:
        """Delete published content"""
        pass
    
    def validate_config(self) -> bool:
        """Validate platform configuration"""
        required_fields = self.get_required_config_fields()
        return all(field in self.config and self.config[field] for field in required_fields)
    
    @abstractmethod
    def get_required_config_fields(self) -> list:
        """Get list of required configuration fields"""
        pass
    
    def get_platform_name(self) -> str:
        """Get platform name"""
        return self.name
