import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
import json

from main import app

client = TestClient(app)


@pytest.fixture
def mock_safe_moderation():
    """Mock safe moderation result"""
    return (True, {"overall_safe": True})


@pytest.fixture
def mock_unsafe_moderation():
    """Mock unsafe moderation result"""
    return (False, {
        "overall_safe": False,
        "openai": {"flagged_categories": ["harassment"]},
        "regex": {"violations": []},
        "blocklist": {"blocked_terms_found": []}
    })


@pytest.fixture
def mock_llm_responses():
    """Mock LLM service responses"""
    return {
        "pickup": [
            "I see you love hiking! What's your favorite trail?",
            "Photography enthusiast here too! What's your go-to camera?",
            "Adventure seeker! What's the most spontaneous trip you've taken?"
        ],
        "reply": [
            "That sounds amazing! I'd love to hear more about it.",
            "Wow, that's really interesting! Tell me more details."
        ]
    }


@patch('backend.routers.generate.moderation_service')
@patch('backend.routers.generate.llm_service')
def test_generate_pickup_success(mock_llm, mock_moderation, mock_safe_moderation, mock_llm_responses):
    """Test successful pickup line generation"""
    # Setup mocks
    mock_moderation.moderate_content = AsyncMock(return_value=mock_safe_moderation)
    mock_llm.generate_multiple = AsyncMock(return_value=mock_llm_responses["pickup"])
    
    # Make request
    response = client.post("/v1/generate", json={
        "mode": "pickup",
        "style": "safe",
        "context": "I love hiking and photography. Always looking for new adventures!"
    })
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "pickup"
    assert data["style"] == "safe"
    assert len(data["choices"]) == 3
    assert all(isinstance(choice, str) for choice in data["choices"])


@patch('backend.routers.generate.moderation_service')
@patch('backend.routers.generate.llm_service')
def test_generate_reply_success(mock_llm, mock_moderation, mock_safe_moderation, mock_llm_responses):
    """Test successful reply generation"""
    # Setup mocks
    mock_moderation.moderate_content = AsyncMock(return_value=mock_safe_moderation)
    mock_llm.generate_multiple = AsyncMock(return_value=mock_llm_responses["reply"])
    
    # Make request
    response = client.post("/v1/generate", json={
        "mode": "reply",
        "style": "funny",
        "context": "Person: I just got back from an amazing trip to Japan!\nMe: That sounds incredible!"
    })
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "reply"
    assert data["style"] == "funny"
    assert len(data["choices"]) == 2


@patch('backend.routers.generate.moderation_service')
def test_generate_unsafe_content(mock_moderation, mock_unsafe_moderation):
    """Test rejection of unsafe content"""
    # Setup mock
    mock_moderation.moderate_content = AsyncMock(return_value=mock_unsafe_moderation)
    
    # Make request with unsafe content
    response = client.post("/v1/generate", json={
        "mode": "pickup",
        "style": "safe",
        "context": "Some inappropriate content here"
    })
    
    # Assertions
    assert response.status_code == 400
    data = response.json()
    assert data["detail"]["code"] == "CONTENT_UNSAFE"
    assert "moderation" in data["detail"]["error"].lower()


def test_generate_invalid_mode():
    """Test invalid generation mode"""
    response = client.post("/v1/generate", json={
        "mode": "invalid_mode",
        "style": "safe",
        "context": "Test content"
    })
    
    # Should fail validation at Pydantic level
    assert response.status_code == 422


def test_generate_empty_context():
    """Test empty context validation"""
    response = client.post("/v1/generate", json={
        "mode": "pickup",
        "style": "safe",
        "context": ""
    })
    
    # Should fail validation due to min_length=1
    assert response.status_code == 422


def test_generate_context_too_long():
    """Test context that's too long"""
    long_context = "x" * 1501  # Exceeds max_length=1500
    
    response = client.post("/v1/generate", json={
        "mode": "pickup",
        "style": "safe",
        "context": long_context
    })
    
    # Should fail validation
    assert response.status_code == 422


@patch('backend.routers.generate.moderation_service')
@patch('backend.routers.generate.llm_service')
def test_generate_with_authorization_header(mock_llm, mock_moderation, mock_safe_moderation, mock_llm_responses):
    """Test generation with authorization header"""
    # Setup mocks
    mock_moderation.moderate_content = AsyncMock(return_value=mock_safe_moderation)
    mock_llm.generate_multiple = AsyncMock(return_value=mock_llm_responses["pickup"])
    
    # Make request with authorization header
    response = client.post(
        "/v1/generate",
        json={
            "mode": "pickup",
            "style": "spicy",
            "context": "I love dancing and good music!"
        },
        headers={"Authorization": "Bearer device-token-123"}
    )
    
    # Should still work (authorization is optional for now)
    assert response.status_code == 200


@patch('backend.routers.generate.moderation_service', None)
@patch('backend.routers.generate.llm_service')
def test_generate_without_moderation_service(mock_llm, mock_llm_responses):
    """Test generation when moderation service is unavailable"""
    # Setup mock
    mock_llm.generate_multiple = AsyncMock(return_value=mock_llm_responses["pickup"])
    
    # Make request
    response = client.post("/v1/generate", json={
        "mode": "pickup",
        "style": "safe",
        "context": "I love books and coffee!"
    })
    
    # Should still work but without moderation
    assert response.status_code == 200


@patch('backend.routers.generate.moderation_service')
@patch('backend.routers.generate.llm_service', None)
def test_generate_without_llm_service(mock_moderation, mock_safe_moderation):
    """Test generation when LLM service is unavailable"""
    # Setup mock
    mock_moderation.moderate_content = AsyncMock(return_value=mock_safe_moderation)
    
    # Make request
    response = client.post("/v1/generate", json={
        "mode": "pickup",
        "style": "safe",
        "context": "I love music and art!"
    })
    
    # Should fail with service unavailable
    assert response.status_code == 503
    data = response.json()
    assert data["detail"]["code"] == "SERVICE_UNAVAILABLE"


@patch('backend.routers.generate.moderation_service')
@patch('backend.routers.generate.llm_service')
def test_generate_llm_error(mock_llm, mock_moderation, mock_safe_moderation):
    """Test handling of LLM service errors"""
    # Setup mocks
    mock_moderation.moderate_content = AsyncMock(return_value=mock_safe_moderation)
    mock_llm.generate_multiple = AsyncMock(side_effect=Exception("LLM service error"))
    
    # Make request
    response = client.post("/v1/generate", json={
        "mode": "pickup",
        "style": "safe",
        "context": "I love traveling!"
    })
    
    # Should fail gracefully
    assert response.status_code == 503
    data = response.json()
    assert data["detail"]["code"] == "GENERATION_FAILED"


@patch('backend.routers.generate.moderation_service')
@patch('backend.routers.generate.llm_service')
def test_generate_insufficient_responses(mock_llm, mock_moderation, mock_safe_moderation):
    """Test handling when LLM generates fewer responses than expected"""
    # Setup mocks
    mock_moderation.moderate_content = AsyncMock(return_value=mock_safe_moderation)
    mock_llm.generate_multiple = AsyncMock(return_value=["Only one response"])  # Should be 3 for pickup
    
    # Make request
    response = client.post("/v1/generate", json={
        "mode": "pickup",
        "style": "safe",
        "context": "I love sports!"
    })
    
    # Should still work with fallback responses
    assert response.status_code == 200
    data = response.json()
    assert len(data["choices"]) == 3  # Should be padded to expected count


def test_generate_all_styles():
    """Test all style presets are accepted"""
    styles = ["safe", "spicy", "funny"]
    
    for style in styles:
        response = client.post("/v1/generate", json={
            "mode": "pickup",
            "style": style,
            "context": "I love reading!"
        })
        
        # Should not fail validation (actual generation may fail due to missing services)
        assert response.status_code in [200, 503]  # 503 if services not available


def test_generate_default_style():
    """Test that default style is applied when not specified"""
    response = client.post("/v1/generate", json={
        "mode": "pickup",
        "context": "I love music!"
        # style not specified, should default to "safe"
    })
    
    # Should not fail validation
    assert response.status_code in [200, 503]