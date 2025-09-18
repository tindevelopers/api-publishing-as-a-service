"""
Content validation service
"""

import re
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from app.models.content import AIContent, ContentValidationResult, ContentType, ContentStatus
from app.config import get_settings


class ContentValidator:
    """Content validation service"""
    
    def __init__(self):
        self.settings = get_settings()
        self._setup_validation_rules()
    
    def _setup_validation_rules(self):
        """Setup validation rules"""
        self.rules = {
            'title': {
                'min_length': 1,
                'max_length': 200,
                'required': True
            },
            'content': {
                'min_length': 1,
                'max_length': self.settings.max_content_length,
                'required': True
            },
            'excerpt': {
                'max_length': 500,
                'required': False
            },
            'tags': {
                'max_count': 20,
                'max_length_per_tag': 50,
                'required': False
            },
            'categories': {
                'max_count': 10,
                'max_length_per_category': 100,
                'required': False
            },
            'images': {
                'max_count': self.settings.max_images_per_content,
                'allowed_types': self.settings.allowed_image_types,
                'required': False
            }
        }
    
    def validate_content(self, content: AIContent) -> ContentValidationResult:
        """Validate content and return validation result"""
        errors = []
        warnings = []
        
        # Basic field validation
        self._validate_basic_fields(content, errors, warnings)
        
        # Content-specific validation
        self._validate_content_type_specific(content, errors, warnings)
        
        # SEO validation
        self._validate_seo(content, errors, warnings)
        
        # HTML content validation
        self._validate_html_content(content, errors, warnings)
        
        # Image validation
        self._validate_images(content, errors, warnings)
        
        # Calculate validation score
        score = self._calculate_validation_score(content, errors, warnings)
        
        return ContentValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            score=score
        )
    
    def _validate_basic_fields(self, content: AIContent, errors: List[Dict[str, str]], warnings: List[Dict[str, str]]):
        """Validate basic content fields"""
        
        # Title validation
        if not content.title or not content.title.strip():
            errors.append({
                'field': 'title',
                'message': 'Title is required and cannot be empty'
            })
        elif len(content.title) > self.rules['title']['max_length']:
            errors.append({
                'field': 'title',
                'message': f'Title must be {self.rules["title"]["max_length"]} characters or less'
            })
        elif len(content.title) < 10:
            warnings.append({
                'field': 'title',
                'message': 'Title is quite short, consider making it more descriptive'
            })
        
        # Content validation
        if not content.content or not content.content.strip():
            errors.append({
                'field': 'content',
                'message': 'Content is required and cannot be empty'
            })
        elif len(content.content) > self.rules['content']['max_length']:
            errors.append({
                'field': 'content',
                'message': f'Content exceeds maximum length of {self.rules["content"]["max_length"]} characters'
            })
        elif len(content.content) < 100:
            warnings.append({
                'field': 'content',
                'message': 'Content is quite short, consider adding more detail'
            })
        
        # Excerpt validation
        if content.excerpt and len(content.excerpt) > self.rules['excerpt']['max_length']:
            errors.append({
                'field': 'excerpt',
                'message': f'Excerpt must be {self.rules["excerpt"]["max_length"]} characters or less'
            })
        
        # Tags validation
        if content.tags:
            if len(content.tags) > self.rules['tags']['max_count']:
                errors.append({
                    'field': 'tags',
                    'message': f'Maximum {self.rules["tags"]["max_count"]} tags allowed'
                })
            
            for i, tag in enumerate(content.tags):
                if len(tag) > self.rules['tags']['max_length_per_tag']:
                    errors.append({
                        'field': f'tags[{i}]',
                        'message': f'Tag must be {self.rules["tags"]["max_length_per_tag"]} characters or less'
                    })
        
        # Categories validation
        if content.categories:
            if len(content.categories) > self.rules['categories']['max_count']:
                errors.append({
                    'field': 'categories',
                    'message': f'Maximum {self.rules["categories"]["max_count"]} categories allowed'
                })
            
            for i, category in enumerate(content.categories):
                if len(category) > self.rules['categories']['max_length_per_category']:
                    errors.append({
                        'field': f'categories[{i}]',
                        'message': f'Category must be {self.rules["categories"]["max_length_per_category"]} characters or less'
                    })
    
    def _validate_content_type_specific(self, content: AIContent, errors: List[Dict[str, str]], warnings: List[Dict[str, str]]):
        """Validate content type specific fields"""
        
        if content.type == ContentType.FAQ:
            if not content.faqs:
                errors.append({
                    'field': 'faqs',
                    'message': 'FAQ content must include at least one FAQ item'
                })
            else:
                self._validate_faqs(content.faqs, errors, warnings)
        
        elif content.type == ContentType.PRODUCT_DESCRIPTION:
            if not content.specifications:
                warnings.append({
                    'field': 'specifications',
                    'message': 'Product descriptions typically include specifications'
                })
            else:
                self._validate_specifications(content.specifications, errors, warnings)
        
        elif content.type == ContentType.LANDING_PAGE:
            if not content.cta_text or not content.cta_url:
                warnings.append({
                    'field': 'cta',
                    'message': 'Landing pages typically include a call-to-action'
                })
    
    def _validate_faqs(self, faqs: List, errors: List[Dict[str, str]], warnings: List[Dict[str, str]]):
        """Validate FAQ items"""
        if len(faqs) == 0:
            errors.append({
                'field': 'faqs',
                'message': 'At least one FAQ item is required'
            })
            return
        
        if len(faqs) > 50:
            errors.append({
                'field': 'faqs',
                'message': 'Maximum 50 FAQ items allowed'
            })
        
        for i, faq in enumerate(faqs):
            if not faq.question or not faq.question.strip():
                errors.append({
                    'field': f'faqs[{i}].question',
                    'message': 'FAQ question is required'
                })
            elif len(faq.question) > 500:
                errors.append({
                    'field': f'faqs[{i}].question',
                    'message': 'FAQ question must be 500 characters or less'
                })
            
            if not faq.answer or not faq.answer.strip():
                errors.append({
                    'field': f'faqs[{i}].answer',
                    'message': 'FAQ answer is required'
                })
            elif len(faq.answer) > 2000:
                errors.append({
                    'field': f'faqs[{i}].answer',
                    'message': 'FAQ answer must be 2000 characters or less'
                })
            
            if faq.order < 1:
                errors.append({
                    'field': f'faqs[{i}].order',
                    'message': 'FAQ order must be 1 or greater'
                })
    
    def _validate_specifications(self, specifications: List, errors: List[Dict[str, str]], warnings: List[Dict[str, str]]):
        """Validate product specifications"""
        if len(specifications) > 100:
            errors.append({
                'field': 'specifications',
                'message': 'Maximum 100 specifications allowed'
            })
        
        for i, spec in enumerate(specifications):
            if not spec.name or not spec.name.strip():
                errors.append({
                    'field': f'specifications[{i}].name',
                    'message': 'Specification name is required'
                })
            elif len(spec.name) > 100:
                errors.append({
                    'field': f'specifications[{i}].name',
                    'message': 'Specification name must be 100 characters or less'
                })
            
            if not spec.value or not spec.value.strip():
                errors.append({
                    'field': f'specifications[{i}].value',
                    'message': 'Specification value is required'
                })
            elif len(spec.value) > 200:
                errors.append({
                    'field': f'specifications[{i}].value',
                    'message': 'Specification value must be 200 characters or less'
                })
    
    def _validate_seo(self, content: AIContent, errors: List[Dict[str, str]], warnings: List[Dict[str, str]]):
        """Validate SEO configuration"""
        if not content.seo:
            warnings.append({
                'field': 'seo',
                'message': 'SEO configuration is recommended for better search visibility'
            })
            return
        
        seo = content.seo
        
        # Meta title validation
        if seo.meta_title:
            if len(seo.meta_title) > 60:
                errors.append({
                    'field': 'seo.meta_title',
                    'message': 'Meta title should be 60 characters or less for optimal SEO'
                })
            elif len(seo.meta_title) < 30:
                warnings.append({
                    'field': 'seo.meta_title',
                    'message': 'Meta title is quite short, consider making it more descriptive'
                })
        else:
            warnings.append({
                'field': 'seo.meta_title',
                'message': 'Meta title is recommended for SEO'
            })
        
        # Meta description validation
        if seo.meta_description:
            if len(seo.meta_description) > 160:
                errors.append({
                    'field': 'seo.meta_description',
                    'message': 'Meta description should be 160 characters or less for optimal SEO'
                })
            elif len(seo.meta_description) < 120:
                warnings.append({
                    'field': 'seo.meta_description',
                    'message': 'Meta description is quite short, consider making it more descriptive'
                })
        else:
            warnings.append({
                'field': 'seo.meta_description',
                'message': 'Meta description is recommended for SEO'
            })
        
        # Keywords validation
        if seo.keywords:
            if len(seo.keywords) > 20:
                warnings.append({
                    'field': 'seo.keywords',
                    'message': 'Too many keywords may dilute SEO effectiveness'
                })
    
    def _validate_html_content(self, content: AIContent, errors: List[Dict[str, str]], warnings: List[Dict[str, str]]):
        """Validate HTML content structure"""
        try:
            soup = BeautifulSoup(content.content, 'html.parser')
            
            # Check for basic HTML structure
            if not soup.get_text().strip():
                errors.append({
                    'field': 'content',
                    'message': 'Content appears to be empty after HTML parsing'
                })
            
            # Check for images without alt text
            images_without_alt = soup.find_all('img', alt='')
            if images_without_alt:
                warnings.append({
                    'field': 'content',
                    'message': f'Found {len(images_without_alt)} images without alt text for accessibility'
                })
            
            # Check for links without text
            empty_links = soup.find_all('a', string='')
            if empty_links:
                warnings.append({
                    'field': 'content',
                    'message': f'Found {len(empty_links)} empty links'
                })
            
            # Check for heading structure
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            if not headings:
                warnings.append({
                    'field': 'content',
                    'message': 'Content has no headings, consider adding structure'
                })
            
            # Check for multiple h1 tags
            h1_tags = soup.find_all('h1')
            if len(h1_tags) > 1:
                warnings.append({
                    'field': 'content',
                    'message': 'Multiple H1 tags found, consider using only one for SEO'
                })
            
        except Exception as e:
            errors.append({
                'field': 'content',
                'message': f'Invalid HTML content: {str(e)}'
            })
    
    def _validate_images(self, content: AIContent, errors: List[Dict[str, str]], warnings: List[Dict[str, str]]):
        """Validate images"""
        if not content.images:
            return
        
        if len(content.images) > self.rules['images']['max_count']:
            errors.append({
                'field': 'images',
                'message': f'Maximum {self.rules["images"]["max_count"]} images allowed'
            })
        
        for i, image in enumerate(content.images):
            if not image.alt_text:
                warnings.append({
                    'field': f'images[{i}].alt_text',
                    'message': 'Image alt text is recommended for accessibility'
                })
            
            if not image.url:
                errors.append({
                    'field': f'images[{i}].url',
                    'message': 'Image URL is required'
                })
    
    def _calculate_validation_score(self, content: AIContent, errors: List[Dict[str, str]], warnings: List[Dict[str, str]]) -> int:
        """Calculate validation score out of 100"""
        base_score = 100
        
        # Deduct points for errors (more severe)
        error_penalty = len(errors) * 10
        warning_penalty = len(warnings) * 2
        
        # Bonus points for good practices
        bonus = 0
        if content.seo and content.seo.meta_title and content.seo.meta_description:
            bonus += 5
        if content.tags and len(content.tags) > 0:
            bonus += 3
        if content.categories and len(content.categories) > 0:
            bonus += 2
        if content.images and all(img.alt_text for img in content.images):
            bonus += 5
        
        score = max(0, min(100, base_score - error_penalty - warning_penalty + bonus))
        return score
    
    def validate_for_platform(self, content: AIContent, platform: str) -> ContentValidationResult:
        """Validate content for specific platform requirements"""
        base_result = self.validate_content(content)
        
        if not base_result.is_valid:
            return base_result
        
        platform_errors = []
        platform_warnings = []
        
        # Platform-specific validation
        if platform == "twitter":
            if len(content.title) > 280:
                platform_errors.append({
                    'field': 'title',
                    'message': 'Title too long for Twitter (280 character limit)'
                })
        
        elif platform == "linkedin":
            if content.content and len(content.content) > 3000:
                platform_warnings.append({
                    'field': 'content',
                    'message': 'Content is quite long for LinkedIn posts'
                })
        
        elif platform == "webflow":
            if not content.seo:
                platform_warnings.append({
                    'field': 'seo',
                    'message': 'SEO configuration is important for Webflow sites'
                })
        
        # Combine results
        all_errors = base_result.errors + platform_errors
        all_warnings = base_result.warnings + platform_warnings
        
        return ContentValidationResult(
            is_valid=len(all_errors) == 0,
            errors=all_errors,
            warnings=all_warnings,
            score=max(0, base_result.score - len(platform_errors) * 5 - len(platform_warnings))
        )
