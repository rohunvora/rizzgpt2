import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from openai.types.chat import ChatCompletion, ChatCompletionMessage
from openai.types.chat.chat_completion import Choice

from backend.services.llm import LLMService


@pytest.fixture
def mock_openai_response():
    """Create a mock OpenAI chat completion response"""
    return ChatCompletion(
        id="test-id",
        choices=[
            Choice(
                finish_reason="stop",
                index=0,
                message=ChatCompletionMessage(
                    content="Test response",
                    role="assistant",
                ),
            )
        ],
        created=1234567890,
        model="gpt-4o",
        object="chat.completion",
    )


@pytest.fixture
def mock_openai_multiple_response():
    """Create a mock OpenAI response with multiple choices"""
    return ChatCompletion(
        id="test-id",
        choices=[
            Choice(
                finish_reason="stop",
                index=0,
                message=ChatCompletionMessage(
                    content="Response 1",
                    role="assistant",
                ),
            ),
            Choice(
                finish_reason="stop",
                index=1,
                message=ChatCompletionMessage(
                    content="Response 2",
                    role="assistant",
                ),
            ),
            Choice(
                finish_reason="stop",
                index=2,
                message=ChatCompletionMessage(
                    content="Response 3",
                    role="assistant",
                ),
            ),
        ],
        created=1234567890,
        model="gpt-4o",
        object="chat.completion",
    )


@pytest.mark.asyncio
async def test_llm_service_initialization():
    """Test LLMService initializes with API key"""
    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
        service = LLMService()
        assert service.client is not None


@pytest.mark.asyncio
async def test_llm_service_no_api_key():
    """Test LLMService raises error when no API key is provided"""
    with patch.dict("os.environ", {}, clear=True):
        with patch("backend.services.llm.settings.openai_api_key", ""):
            with pytest.raises(ValueError, match="OpenAI API key not found"):
                LLMService()


@pytest.mark.asyncio
async def test_generate_completion(mock_openai_response):
    """Test single completion generation"""
    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
        service = LLMService()
        
        # Mock the OpenAI client
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_openai_response)
        service.client = mock_client
        
        messages = [{"role": "user", "content": "Test prompt"}]
        result = await service.generate_completion(messages)
        
        assert result == "Test response"
        mock_client.chat.completions.create.assert_called_once()


@pytest.mark.asyncio
async def test_generate_multiple(mock_openai_multiple_response):
    """Test multiple completions generation"""
    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
        service = LLMService()
        
        # Mock the OpenAI client
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_openai_multiple_response)
        service.client = mock_client
        
        messages = [{"role": "user", "content": "Test prompt"}]
        results = await service.generate_multiple(messages, count=3)
        
        assert len(results) == 3
        assert results == ["Response 1", "Response 2", "Response 3"]
        mock_client.chat.completions.create.assert_called_once()


@pytest.mark.asyncio
async def test_api_error_handling():
    """Test error handling for API failures"""
    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
        service = LLMService()
        
        # Mock the OpenAI client to raise an exception
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(
            side_effect=Exception("API Error")
        )
        service.client = mock_client
        
        messages = [{"role": "user", "content": "Test prompt"}]
        
        with pytest.raises(RuntimeError, match="OpenAI API error: API Error"):
            await service.generate_completion(messages)


@pytest.mark.asyncio
async def test_streaming_completion():
    """Test streaming completion generation"""
    # Create mock stream chunks
    mock_chunks = [
        MagicMock(choices=[MagicMock(delta=MagicMock(content="Hello"))]),
        MagicMock(choices=[MagicMock(delta=MagicMock(content=" world"))]),
        MagicMock(choices=[MagicMock(delta=MagicMock(content="!"))]),
    ]
    
    async def mock_stream():
        for chunk in mock_chunks:
            yield chunk
    
    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
        service = LLMService()
        
        # Mock the OpenAI client
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_stream())
        service.client = mock_client
        
        messages = [{"role": "user", "content": "Test prompt"}]
        stream = await service.generate_completion(messages, stream=True)
        
        # Collect streamed content
        content = []
        async for chunk in stream:
            content.append(chunk)
        
        assert content == ["Hello", " world", "!"]