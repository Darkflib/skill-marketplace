"""
Pytest configuration and shared fixtures for {{PROJECT_NAME}}
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def mock_db():
    """Mock database connection."""
    # Example: Set up test database
    # yield db_connection
    # Clean up
    pass


@pytest.fixture
def sample_item():
    """Sample item data for testing."""
    return {
        "id": 1,
        "name": "Test Item",
        "description": "A test item",
    }
