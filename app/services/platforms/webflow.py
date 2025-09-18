"""
Webflow platform service
"""

import httpx
from typing import Dict, Any, Optional
from datetime import datetime
from app.models.content import AIContent, PublishResponse
from app.services.platforms.base import BasePlatformService
from app.config import get_settings


class WebflowService(BasePlatformService):
    """Webflow publishing service"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get('api_key')
        self.site_id = config.get('site_id')
        self.collection_id = config.get('collection_id')
        self.base_url = "https://api.webflow.com/v2"
        self.settings = get_settings()
    
    def get_required_config_fields(self) -> list:
        """Get required configuration fields"""
        return ['api_key', 'site_id']
    
    async def test_connection(self) -> bool:
        """Test Webflow API connection"""
        try:
            async with httpx.AsyncClient(timeout=self.settings.default_timeout) as client:
                headers = {"Authorization": f"Bearer {self.api_key}"}
                response = await client.get(f"{self.base_url}/sites/{self.site_id}", headers=headers)
                return response.status_code == 200
        except Exception:
            return False
    
    async def publish(self, content: AIContent, options: Optional[Dict[str, Any]] = None) -> PublishResponse:
        """Publish content to Webflow"""
        try:
            if not self.validate_config():
                return PublishResponse(
                    success=False,
                    message="Invalid Webflow configuration",
                    errors=["Missing required configuration fields"]
                )
            
            # Prepare content data for Webflow
            webflow_data = self._prepare_webflow_data(content, options)
            
            async with httpx.AsyncClient(timeout=self.settings.default_timeout) as client:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                # Create item in collection
                response = await client.post(
                    f"{self.base_url}/collections/{self.collection_id}/items",
                    headers=headers,
                    json=webflow_data
                )
                
                if response.status_code == 201:
                    item_data = response.json()
                    return PublishResponse(
                        success=True,
                        message="Content published successfully to Webflow",
                        content_id=item_data.get('id'),
                        url=item_data.get('url'),
                        published_at=datetime.utcnow()
                    )
                else:
                    error_data = response.json()
                    return PublishResponse(
                        success=False,
                        message=f"Failed to publish to Webflow: {error_data.get('msg', 'Unknown error')}",
                        errors=[error_data.get('msg', 'Unknown error')]
                    )
        
        except httpx.TimeoutException:
            return PublishResponse(
                success=False,
                message="Request timeout while publishing to Webflow",
                errors=["Request timeout"]
            )
        except Exception as e:
            return PublishResponse(
                success=False,
                message=f"Error publishing to Webflow: {str(e)}",
                errors=[str(e)]
            )
    
    def _prepare_webflow_data(self, content: AIContent, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Prepare content data for Webflow API"""
        data = {
            "isArchived": False,
            "isDraft": content.status == "draft",
            "fieldData": {
                "name": content.title,
                "slug": self._generate_slug(content.title),
                "post-body": content.content,
                "post-summary": content.excerpt or "",
                "main-image": content.featured_image.url if content.featured_image else "",
                "category": content.categories[0] if content.categories else "",
                "tags": content.tags or [],
                "author": content.author or "AI Content Publisher",
                "publish-date": content.publish_date.isoformat() if content.publish_date else datetime.utcnow().isoformat(),
            }
        }
        
        # Add SEO fields if available
        if content.seo:
            if content.seo.meta_title:
                data["fieldData"]["seo-title"] = content.seo.meta_title
            if content.seo.meta_description:
                data["fieldData"]["seo-description"] = content.seo.meta_description
            if content.seo.keywords:
                data["fieldData"]["seo-keywords"] = ", ".join(content.seo.keywords)
        
        # Add custom fields from options
        if options and "custom_fields" in options:
            data["fieldData"].update(options["custom_fields"])
        
        return data
    
    def _generate_slug(self, title: str) -> str:
        """Generate URL slug from title"""
        import re
        from urllib.parse import quote
        
        # Convert to lowercase and replace spaces with hyphens
        slug = re.sub(r'[^\w\s-]', '', title.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')
    
    async def get_content(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Get published content by ID"""
        try:
            async with httpx.AsyncClient(timeout=self.settings.default_timeout) as client:
                headers = {"Authorization": f"Bearer {self.api_key}"}
                response = await client.get(
                    f"{self.base_url}/collections/{self.collection_id}/items/{content_id}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    return response.json()
                return None
        
        except Exception:
            return None
    
    async def update_content(self, content_id: str, content: AIContent, options: Optional[Dict[str, Any]] = None) -> PublishResponse:
        """Update published content"""
        try:
            webflow_data = self._prepare_webflow_data(content, options)
            
            async with httpx.AsyncClient(timeout=self.settings.default_timeout) as client:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                response = await client.patch(
                    f"{self.base_url}/collections/{self.collection_id}/items/{content_id}",
                    headers=headers,
                    json=webflow_data
                )
                
                if response.status_code == 200:
                    item_data = response.json()
                    return PublishResponse(
                        success=True,
                        message="Content updated successfully in Webflow",
                        content_id=item_data.get('id'),
                        url=item_data.get('url'),
                        published_at=datetime.utcnow()
                    )
                else:
                    error_data = response.json()
                    return PublishResponse(
                        success=False,
                        message=f"Failed to update content in Webflow: {error_data.get('msg', 'Unknown error')}",
                        errors=[error_data.get('msg', 'Unknown error')]
                    )
        
        except Exception as e:
            return PublishResponse(
                success=False,
                message=f"Error updating content in Webflow: {str(e)}",
                errors=[str(e)]
            )
    
    async def delete_content(self, content_id: str) -> bool:
        """Delete published content"""
        try:
            async with httpx.AsyncClient(timeout=self.settings.default_timeout) as client:
                headers = {"Authorization": f"Bearer {self.api_key}"}
                response = await client.delete(
                    f"{self.base_url}/collections/{self.collection_id}/items/{content_id}",
                    headers=headers
                )
                
                return response.status_code == 204
        
        except Exception:
            return False
