import pytest
from fastapi.testclient import TestClient
from main import app


client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint returns expected response"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "RizzGPT Clone API"
    assert data["version"] == "1.0.0"


def test_health_check():
    """Test health check endpoint returns 200 and healthy status"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "environment" in data