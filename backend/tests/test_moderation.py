import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from openai.types.moderation import Moderation, ModerationResult, Categories, CategoryScores

from backend.services.moderation import ModerationService


@pytest.fixture
def mock_safe_moderation_response():
    """Create a mock safe OpenAI moderation response"""
    return Moderation(
        id="test-mod-id",
        model="text-moderation-007",
        results=[
            ModerationResult(
                flagged=False,
                categories=Categories(
                    harassment=False,
                    harassment_threatening=False,
                    hate=False,
                    hate_threatening=False,
                    self_harm=False,
                    self_harm_instructions=False,
                    self_harm_intent=False,
                    sexual=False,
                    sexual_minors=False,
                    violence=False,
                    violence_graphic=False,
                ),
                category_scores=CategoryScores(
                    harassment=0.1,
                    harassment_threatening=0.05,
                    hate=0.02,
                    hate_threatening=0.01,
                    self_harm=0.0,
                    self_harm_instructions=0.0,
                    self_harm_intent=0.0,
                    sexual=0.03,
                    sexual_minors=0.0,
                    violence=0.02,
                    violence_graphic=0.01,
                ),
            )
        ],
    )


@pytest.fixture
def mock_unsafe_moderation_response():
    """Create a mock unsafe OpenAI moderation response"""
    return Moderation(
        id="test-mod-id",
        model="text-moderation-007",
        results=[
            ModerationResult(
                flagged=True,
                categories=Categories(
                    harassment=True,
                    harassment_threatening=False,
                    hate=False,
                    hate_threatening=False,
                    self_harm=False,
                    self_harm_instructions=False,
                    self_harm_intent=False,
                    sexual=True,
                    sexual_minors=False,
                    violence=False,
                    violence_graphic=False,
                ),
                category_scores=CategoryScores(
                    harassment=0.95,  # Above threshold
                    harassment_threatening=0.05,
                    hate=0.02,
                    hate_threatening=0.01,
                    self_harm=0.0,
                    self_harm_instructions=0.0,
                    self_harm_intent=0.0,
                    sexual=0.92,  # Above threshold
                    sexual_minors=0.0,
                    violence=0.02,
                    violence_graphic=0.01,
                ),
            )
        ],
    )


@pytest.mark.asyncio
async def test_moderation_service_initialization():
    """Test ModerationService initializes properly"""
    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
        service = ModerationService()
        assert service.client is not None


@pytest.mark.asyncio
async def test_safe_content_moderation(mock_safe_moderation_response):
    """Test moderation of safe content"""
    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
        service = ModerationService()
        
        # Mock the OpenAI client
        mock_client = AsyncMock()
        mock_client.moderations.create = AsyncMock(return_value=mock_safe_moderation_response)
        service.client = mock_client
        
        is_safe, details = await service.moderate_content("Hello, how are you today?")
        
        assert is_safe is True
        assert details["overall_safe"] is True
        assert details["openai"]["flagged"] is False
        assert len(details["openai"]["flagged_categories"]) == 0


@pytest.mark.asyncio
async def test_unsafe_content_moderation(mock_unsafe_moderation_response):
    """Test moderation of unsafe content"""
    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
        service = ModerationService()
        
        # Mock the OpenAI client
        mock_client = AsyncMock()
        mock_client.moderations.create = AsyncMock(return_value=mock_unsafe_moderation_response)
        service.client = mock_client
        
        is_safe, details = await service.moderate_content("Inappropriate content here")
        
        assert is_safe is False
        assert details["overall_safe"] is False
        assert details["openai"]["flagged"] is True
        assert "harassment" in details["openai"]["flagged_categories"]
        assert "sexual" in details["openai"]["flagged_categories"]


@pytest.mark.asyncio
async def test_phone_number_detection():
    """Test phone number regex detection"""
    service = ModerationService()
    
    test_cases = [
        ("Call me at 555-123-4567", False),
        ("My number is (555) 123-4567", False),
        ("Reach me at +1-555-123-4567", False),
        ("Hello there, nice to meet you", True),
    ]
    
    for text, should_be_safe in test_cases:
        is_safe, details = await service._regex_filters(text)
        assert is_safe == should_be_safe
        if not should_be_safe:
            assert "phone_number" in details["violations"]


@pytest.mark.asyncio
async def test_address_detection():
    """Test address regex detection"""
    service = ModerationService()
    
    test_cases = [
        ("I live at 123 Main Street", False),
        ("Visit me at 456 Oak Avenue", False),
        ("My address is 789 Elm Drive", False),
        ("Let's meet somewhere nice", True),
    ]
    
    for text, should_be_safe in test_cases:
        is_safe, details = await service._regex_filters(text)
        assert is_safe == should_be_safe
        if not should_be_safe:
            assert "address" in details["violations"]


@pytest.mark.asyncio
async def test_email_detection():
    """Test email regex detection"""
    service = ModerationService()
    
    test_cases = [
        ("Email me at john@example.com", False),
        ("My email is user.name@domain.org", False),
        ("Contact: test123@gmail.com", False),
        ("Let's chat here instead", True),
    ]
    
    for text, should_be_safe in test_cases:
        is_safe, details = await service._regex_filters(text)
        assert is_safe == should_be_safe
        if not should_be_safe:
            assert "email" in details["violations"]


@pytest.mark.asyncio
async def test_blocklist_detection():
    """Test blocked terms detection"""
    service = ModerationService()
    
    test_cases = [
        ("I'm underage", False),
        ("Violence is not okay", False),
        ("This contains harmful content", False),
        ("Let's have a nice conversation", True),
    ]
    
    for text, should_be_safe in test_cases:
        is_safe, details = await service._blocklist_check(text)
        assert is_safe == should_be_safe
        if not should_be_safe:
            assert len(details["blocked_terms_found"]) > 0


@pytest.mark.asyncio
async def test_empty_content():
    """Test moderation of empty content"""
    service = ModerationService()
    
    test_cases = ["", "   ", "\n\t", None]
    
    for text in test_cases:
        is_safe, details = await service.moderate_content(text or "")
        assert is_safe is True
        assert details["reason"] == "empty_content"


@pytest.mark.asyncio
async def test_api_error_handling():
    """Test handling of OpenAI API errors"""
    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
        service = ModerationService()
        
        # Mock the OpenAI client to raise an exception
        mock_client = AsyncMock()
        mock_client.moderations.create = AsyncMock(side_effect=Exception("API Error"))
        service.client = mock_client
        
        is_safe, details = await service.moderate_content("Test content")
        
        # Should be safe (conservative approach) when API fails
        assert details["openai"]["error"].startswith("moderation_api_error")


@pytest.mark.asyncio
async def test_add_remove_blocked_terms():
    """Test adding and removing blocked terms"""
    service = ModerationService()
    
    initial_count = len(service.BLOCKED_TERMS)
    
    # Add new term
    service.add_blocked_term("newbadword")
    assert len(service.BLOCKED_TERMS) == initial_count + 1
    assert "newbadword" in service.BLOCKED_TERMS
    
    # Try to add duplicate (should not increase count)
    service.add_blocked_term("newbadword")
    assert len(service.BLOCKED_TERMS) == initial_count + 1
    
    # Remove term
    service.remove_blocked_term("newbadword")
    assert len(service.BLOCKED_TERMS) == initial_count
    assert "newbadword" not in service.BLOCKED_TERMS


@pytest.mark.asyncio
async def test_comprehensive_moderation_flow(mock_safe_moderation_response):
    """Test complete moderation flow with all checks"""
    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
        service = ModerationService()
        
        # Mock the OpenAI client
        mock_client = AsyncMock()
        mock_client.moderations.create = AsyncMock(return_value=mock_safe_moderation_response)
        service.client = mock_client
        
        # Test safe content
        is_safe, details = await service.moderate_content("Hello, nice to meet you!")
        
        assert is_safe is True
        assert "openai" in details
        assert "regex" in details
        assert "blocklist" in details
        assert details["overall_safe"] is True