"""
Unit tests for Pydantic models
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from app.models.content import (
    AIContent, ContentType, ContentStatus, ContentImage, 
    SEOConfig, FAQItem, ProductSpecification
)


class TestAIContent:
    """Test AIContent model validation."""
    
    def test_valid_content_creation(self, sample_content):
        """Test creating valid content."""
        content = AIContent(**sample_content)
        
        assert content.type == ContentType.BLOG
        assert content.title == "Test Blog Post"
        assert content.status == ContentStatus.DRAFT
        assert len(content.tags) == 2
        assert len(content.categories) == 1
    
    def test_content_type_validation(self):
        """Test content type validation."""
        content_data = {
            "type": "invalid_type",  # Invalid type
            "title": "Test Title",
            "content": "<p>Test content</p>"
        }
        
        with pytest.raises(ValidationError):
            AIContent(**content_data)
    
    def test_title_validation(self):
        """Test title validation."""
        # Empty title
        with pytest.raises(ValidationError):
            AIContent(
                type="blog",
                title="",
                content="<p>Test content</p>"
            )
        
        # Title too long
        with pytest.raises(ValidationError):
            AIContent(
                type="blog",
                title="A" * 201,  # Exceeds 200 char limit
                content="<p>Test content</p>"
            )
    
    def test_tags_validation(self):
        """Test tags validation."""
        content_data = {
            "type": "blog",
            "title": "Test Title",
            "content": "<p>Test content</p>",
            "tags": ["tag1", "tag2", "tag3"] * 10  # Too many tags
        }
        
        with pytest.raises(ValidationError):
            AIContent(**content_data)
    
    def test_faq_content_type(self):
        """Test FAQ content type with FAQs."""
        content_data = {
            "type": "faq",
            "title": "FAQ Test",
            "content": "<p>FAQ content</p>",
            "faqs": [
                {
                    "question": "What is this?",
                    "answer": "This is a test",
                    "order": 1
                }
            ]
        }
        
        content = AIContent(**content_data)
        assert content.type == ContentType.FAQ
        assert len(content.faqs) == 1
        assert content.faqs[0].question == "What is this?"
    
    def test_product_description_type(self):
        """Test product description content type."""
        content_data = {
            "type": "product-description",
            "title": "Product Test",
            "content": "<p>Product content</p>",
            "specifications": [
                {
                    "name": "Weight",
                    "value": "1kg",
                    "unit": "kg"
                }
            ]
        }
        
        content = AIContent(**content_data)
        assert content.type == ContentType.PRODUCT_DESCRIPTION
        assert len(content.specifications) == 1
        assert content.specifications[0].name == "Weight"


class TestSEOConfig:
    """Test SEO configuration model."""
    
    def test_valid_seo_config(self):
        """Test valid SEO configuration."""
        seo = SEOConfig(
            meta_title="Test Title",
            meta_description="Test description",
            keywords=["test", "seo"]
        )
        
        assert seo.meta_title == "Test Title"
        assert seo.meta_description == "Test description"
        assert len(seo.keywords) == 2
    
    def test_meta_title_length_validation(self):
        """Test meta title length validation."""
        with pytest.raises(ValidationError):
            SEOConfig(meta_title="A" * 61)  # Exceeds 60 char limit
    
    def test_meta_description_length_validation(self):
        """Test meta description length validation."""
        with pytest.raises(ValidationError):
            SEOConfig(meta_description="A" * 161)  # Exceeds 160 char limit


class TestFAQItem:
    """Test FAQ item model."""
    
    def test_valid_faq_item(self):
        """Test valid FAQ item creation."""
        faq = FAQItem(
            question="What is this?",
            answer="This is a test FAQ",
            order=1
        )
        
        assert faq.question == "What is this?"
        assert faq.answer == "This is a test FAQ"
        assert faq.order == 1
    
    def test_faq_question_validation(self):
        """Test FAQ question validation."""
        with pytest.raises(ValidationError):
            FAQItem(
                question="",  # Empty question
                answer="Valid answer",
                order=1
            )
    
    def test_faq_answer_validation(self):
        """Test FAQ answer validation."""
        with pytest.raises(ValidationError):
            FAQItem(
                question="Valid question",
                answer="",  # Empty answer
                order=1
            )
    
    def test_faq_order_validation(self):
        """Test FAQ order validation."""
        with pytest.raises(ValidationError):
            FAQItem(
                question="Valid question",
                answer="Valid answer",
                order=0  # Invalid order (must be >= 1)
            )


class TestContentImage:
    """Test content image model."""
    
    def test_valid_content_image(self):
        """Test valid content image creation."""
        image = ContentImage(
            url="https://example.com/image.jpg",
            alt_text="Test image"
        )
        
        assert str(image.url) == "https://example.com/image.jpg"
        assert image.alt_text == "Test image"
    
    def test_content_image_validation(self):
        """Test content image validation."""
        with pytest.raises(ValidationError):
            ContentImage(
                url="invalid-url",  # Invalid URL
                alt_text="Test image"
            )
