"""
WordPress platform service
"""

import httpx
import base64
from typing import Dict, Any, Optional
from datetime import datetime
from app.models.content import AIContent, PublishResponse
from app.services.platforms.base import BasePlatformService
from app.config import get_settings


class WordPressService(BasePlatformService):
    """WordPress publishing service"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.site_url = config.get('site_url')
        self.username = config.get('username')
        self.password = config.get('password') or config.get('app_password')
        self.api_url = f"{self.site_url.rstrip('/')}/wp-json/wp/v2"
        self.settings = get_settings()
    
    def get_required_config_fields(self) -> list:
        """Get required configuration fields"""
        return ['site_url', 'username', 'password']
    
    async def test_connection(self) -> bool:
        """Test WordPress API connection"""
        try:
            auth_header = self._get_auth_header()
            async with httpx.AsyncClient(timeout=self.settings.default_timeout) as client:
                response = await client.get(f"{self.api_url}/users/me", headers=auth_header)
                return response.status_code == 200
        except Exception:
            return False
    
    def _get_auth_header(self) -> Dict[str, str]:
        """Get authentication header"""
        credentials = f"{self.username}:{self.password}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        return {"Authorization": f"Basic {encoded_credentials}"}
    
    async def publish(self, content: AIContent, options: Optional[Dict[str, Any]] = None) -> PublishResponse:
        """Publish content to WordPress"""
        try:
            if not self.validate_config():
                return PublishResponse(
                    success=False,
                    message="Invalid WordPress configuration",
                    errors=["Missing required configuration fields"]
                )
            
            # Prepare content data for WordPress
            wp_data = self._prepare_wordpress_data(content, options)
            
            auth_header = self._get_auth_header()
            auth_header["Content-Type"] = "application/json"
            
            async with httpx.AsyncClient(timeout=self.settings.default_timeout) as client:
                response = await client.post(
                    f"{self.api_url}/posts",
                    headers=auth_header,
                    json=wp_data
                )
                
                if response.status_code == 201:
                    post_data = response.json()
                    return PublishResponse(
                        success=True,
                        message="Content published successfully to WordPress",
                        content_id=str(post_data.get('id')),
                        url=post_data.get('link'),
                        published_at=datetime.utcnow()
                    )
                else:
                    error_data = response.json()
                    return PublishResponse(
                        success=False,
                        message=f"Failed to publish to WordPress: {error_data.get('message', 'Unknown error')}",
                        errors=[error_data.get('message', 'Unknown error')]
                    )
        
        except httpx.TimeoutException:
            return PublishResponse(
                success=False,
                message="Request timeout while publishing to WordPress",
                errors=["Request timeout"]
            )
        except Exception as e:
            return PublishResponse(
                success=False,
                message=f"Error publishing to WordPress: {str(e)}",
                errors=[str(e)]
            )
    
    def _prepare_wordpress_data(self, content: AIContent, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Prepare content data for WordPress API"""
        data = {
            "title": content.title,
            "content": content.content,
            "excerpt": content.excerpt or "",
            "status": "publish" if content.status == "published" else "draft",
            "format": "standard",
        }
        
        # Add categories if available
        if content.categories:
            data["categories"] = await self._get_or_create_categories(content.categories)
        
        # Add tags if available
        if content.tags:
            data["tags"] = await self._get_or_create_tags(content.tags)
        
        # Add featured image if available
        if content.featured_image:
            media_id = await self._upload_media(content.featured_image)
            if media_id:
                data["featured_media"] = media_id
        
        # Add SEO data as custom fields
        if content.seo:
            data["meta"] = {
                "_yoast_wpseo_title": content.seo.meta_title or content.title,
                "_yoast_wpseo_metadesc": content.seo.meta_description or content.excerpt,
                "_yoast_wpseo_focuskw": ", ".join(content.seo.keywords) if content.seo.keywords else "",
            }
        
        # Add custom fields from options
        if options and "custom_fields" in options:
            data["meta"].update(options["custom_fields"])
        
        return data
    
    async def _get_or_create_categories(self, categories: list) -> list:
        """Get or create WordPress categories"""
        category_ids = []
        auth_header = self._get_auth_header()
        
        async with httpx.AsyncClient(timeout=self.settings.default_timeout) as client:
            for category_name in categories:
                # First, try to find existing category
                response = await client.get(
                    f"{self.api_url}/categories",
                    headers=auth_header,
                    params={"search": category_name}
                )
                
                if response.status_code == 200:
                    categories_data = response.json()
                    existing_category = next((cat for cat in categories_data if cat['name'].lower() == category_name.lower()), None)
                    
                    if existing_category:
                        category_ids.append(existing_category['id'])
                    else:
                        # Create new category
                        create_response = await client.post(
                            f"{self.api_url}/categories",
                            headers=auth_header,
                            json={"name": category_name}
                        )
                        if create_response.status_code == 201:
                            category_ids.append(create_response.json()['id'])
        
        return category_ids
    
    async def _get_or_create_tags(self, tags: list) -> list:
        """Get or create WordPress tags"""
        tag_ids = []
        auth_header = self._get_auth_header()
        
        async with httpx.AsyncClient(timeout=self.settings.default_timeout) as client:
            for tag_name in tags:
                # First, try to find existing tag
                response = await client.get(
                    f"{self.api_url}/tags",
                    headers=auth_header,
                    params={"search": tag_name}
                )
                
                if response.status_code == 200:
                    tags_data = response.json()
                    existing_tag = next((tag for tag in tags_data if tag['name'].lower() == tag_name.lower()), None)
                    
                    if existing_tag:
                        tag_ids.append(existing_tag['id'])
                    else:
                        # Create new tag
                        create_response = await client.post(
                            f"{self.api_url}/tags",
                            headers=auth_header,
                            json={"name": tag_name}
                        )
                        if create_response.status_code == 201:
                            tag_ids.append(create_response.json()['id'])
        
        return tag_ids
    
    async def _upload_media(self, image) -> Optional[int]:
        """Upload media to WordPress"""
        try:
            auth_header = self._get_auth_header()
            
            async with httpx.AsyncClient(timeout=self.settings.default_timeout) as client:
                # Download image
                image_response = await client.get(str(image.url))
                if image_response.status_code != 200:
                    return None
                
                # Upload to WordPress
                files = {
                    'file': (image.alt_text or 'image', image_response.content, 'image/jpeg')
                }
                
                upload_response = await client.post(
                    f"{self.api_url}/media",
                    headers=auth_header,
                    files=files
                )
                
                if upload_response.status_code == 201:
                    return upload_response.json()['id']
                return None
        
        except Exception:
            return None
    
    async def get_content(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Get published content by ID"""
        try:
            auth_header = self._get_auth_header()
            async with httpx.AsyncClient(timeout=self.settings.default_timeout) as client:
                response = await client.get(
                    f"{self.api_url}/posts/{content_id}",
                    headers=auth_header
                )
                
                if response.status_code == 200:
                    return response.json()
                return None
        
        except Exception:
            return None
    
    async def update_content(self, content_id: str, content: AIContent, options: Optional[Dict[str, Any]] = None) -> PublishResponse:
        """Update published content"""
        try:
            wp_data = self._prepare_wordpress_data(content, options)
            
            auth_header = self._get_auth_header()
            auth_header["Content-Type"] = "application/json"
            
            async with httpx.AsyncClient(timeout=self.settings.default_timeout) as client:
                response = await client.post(
                    f"{self.api_url}/posts/{content_id}",
                    headers=auth_header,
                    json=wp_data
                )
                
                if response.status_code == 200:
                    post_data = response.json()
                    return PublishResponse(
                        success=True,
                        message="Content updated successfully in WordPress",
                        content_id=str(post_data.get('id')),
                        url=post_data.get('link'),
                        published_at=datetime.utcnow()
                    )
                else:
                    error_data = response.json()
                    return PublishResponse(
                        success=False,
                        message=f"Failed to update content in WordPress: {error_data.get('message', 'Unknown error')}",
                        errors=[error_data.get('message', 'Unknown error')]
                    )
        
        except Exception as e:
            return PublishResponse(
                success=False,
                message=f"Error updating content in WordPress: {str(e)}",
                errors=[str(e)]
            )
    
    async def delete_content(self, content_id: str) -> bool:
        """Delete published content"""
        try:
            auth_header = self._get_auth_header()
            async with httpx.AsyncClient(timeout=self.settings.default_timeout) as client:
                response = await client.delete(
                    f"{self.api_url}/posts/{content_id}",
                    headers=auth_header,
                    params={"force": True}
                )
                
                return response.status_code == 200
        
        except Exception:
            return False
