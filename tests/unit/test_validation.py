"""
Unit tests for content validation
"""

import pytest
from app.services.validation import ContentValidator
from app.models.content import AIContent, ContentType, ContentStatus


class TestContentValidator:
    """Test content validation functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = ContentValidator()
    
    def test_valid_content(self, sample_content):
        """Test validation of valid content."""
        content = AIContent(**sample_content)
        result = self.validator.validate_content(content)
        
        assert result.is_valid is True
        assert len(result.errors) == 0
        assert result.score > 0
    
    def test_invalid_title(self):
        """Test validation with invalid title."""
        content_data = {
            "type": "blog",
            "title": "",  # Empty title
            "content": "<p>Valid content</p>",
            "status": "draft"
        }
        content = AIContent(**content_data)
        result = self.validator.validate_content(content)
        
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert any("title" in error["field"] for error in result.errors)
    
    def test_invalid_content(self):
        """Test validation with invalid content."""
        content_data = {
            "type": "blog",
            "title": "Valid Title",
            "content": "",  # Empty content
            "status": "draft"
        }
        content = AIContent(**content_data)
        result = self.validator.validate_content(content)
        
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert any("content" in error["field"] for error in result.errors)
    
    def test_faq_validation(self):
        """Test FAQ content validation."""
        content_data = {
            "type": "faq",
            "title": "FAQ Test",
            "content": "<p>FAQ content</p>",
            "status": "draft",
            "faqs": [
                {
                    "question": "What is this?",
                    "answer": "This is a test FAQ",
                    "order": 1
                }
            ]
        }
        content = AIContent(**content_data)
        result = self.validator.validate_content(content)
        
        assert result.is_valid is True
    
    def test_faq_without_questions(self):
        """Test FAQ content without questions."""
        content_data = {
            "type": "faq",
            "title": "FAQ Test",
            "content": "<p>FAQ content</p>",
            "status": "draft",
            "faqs": []  # Empty FAQs
        }
        content = AIContent(**content_data)
        result = self.validator.validate_content(content)
        
        assert result.is_valid is False
        assert any("faqs" in error["field"] for error in result.errors)
    
    def test_platform_specific_validation(self, sample_content):
        """Test platform-specific validation."""
        content = AIContent(**sample_content)
        
        # Test Twitter validation (character limit)
        result = self.validator.validate_for_platform(content, "twitter")
        assert result.is_valid is True  # Should be valid for short content
        
        # Test with long title for Twitter
        content.title = "A" * 300  # Exceeds Twitter limit
        result = self.validator.validate_for_platform(content, "twitter")
        assert result.is_valid is False
        assert any("twitter" in error["message"].lower() for error in result.errors)
    
    def test_seo_validation(self):
        """Test SEO validation."""
        content_data = {
            "type": "blog",
            "title": "Test Title",
            "content": "<p>Test content</p>",
            "status": "draft",
            "seo": {
                "meta_title": "A" * 100,  # Too long
                "meta_description": "Valid description"
            }
        }
        content = AIContent(**content_data)
        result = self.validator.validate_content(content)
        
        assert result.is_valid is False
        assert any("meta_title" in error["field"] for error in result.errors)
    
    def test_validation_score_calculation(self, sample_content):
        """Test validation score calculation."""
        content = AIContent(**sample_content)
        result = self.validator.validate_content(content)
        
        assert 0 <= result.score <= 100
        assert result.score > 50  # Should have a decent score for valid content
