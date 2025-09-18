"""
Pytest configuration and fixtures
"""

import pytest
import asyncio
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.main import app
from app.config import get_settings


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client for the FastAPI app."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def test_settings():
    """Test settings configuration."""
    return {
        "SECRET_KEY": "test-secret-key",
        "ENVIRONMENT": "testing",
        "DEBUG": True,
        "LOG_LEVEL": "DEBUG",
        "DATABASE_URL": "sqlite:///./test.db",
        "REDIS_URL": "redis://localhost:6379",
    }


@pytest.fixture
def sample_content():
    """Sample content for testing."""
    return {
        "type": "blog",
        "title": "Test Blog Post",
        "content": "<h1>Test Content</h1><p>This is a test blog post.</p>",
        "excerpt": "A test blog post for testing purposes",
        "tags": ["test", "blog"],
        "categories": ["testing"],
        "status": "draft",
        "seo": {
            "meta_title": "Test Blog Post - SEO Title",
            "meta_description": "A test blog post for testing purposes",
            "keywords": ["test", "blog", "testing"]
        }
    }


@pytest.fixture
def sample_publish_request(sample_content):
    """Sample publish request for testing."""
    return {
        "content": sample_content,
        "platforms": ["webflow", "wordpress"],
        "options": {}
    }
