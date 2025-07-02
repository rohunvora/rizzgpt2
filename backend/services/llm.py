import os
from typing import List, AsyncGenerator, Optional, Union
import httpx
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam

from backend.config import settings


class LLMService:
    """Wrapper for OpenAI API with async support and error handling"""
    
    def __init__(self):
        self.client = None
        try:
            self._initialize_client()
        except ValueError:
            # Allow initialization without API key for testing
            pass
    
    def _initialize_client(self):
        """Initialize OpenAI client with API key from settings"""
        api_key = settings.openai_api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key not found in settings or environment")
        
        self.client = AsyncOpenAI(
            api_key=api_key,
            timeout=httpx.Timeout(30.0, connect=5.0),
        )
    
    async def generate_completion(
        self,
        messages: List[ChatCompletionMessageParam],
        model: str = "gpt-4o",
        temperature: float = 0.7,
        max_tokens: int = 150,
        stream: bool = False,
    ) -> Union[str, AsyncGenerator[str, None]]:
        """
        Generate completion from OpenAI
        
        Args:
            messages: List of chat messages
            model: Model to use (default: gpt-4o)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            
        Returns:
            Generated text or async generator for streaming
        """
        if not self.client:
            raise RuntimeError("OpenAI client not initialized")
        
        try:
            if stream:
                return self._stream_completion(
                    messages=messages,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
            else:
                response = await self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    n=1,
                )
                return response.choices[0].message.content or ""
                
        except Exception as e:
            # Log error and re-raise with context
            raise RuntimeError(f"OpenAI API error: {str(e)}") from e
    
    async def _stream_completion(
        self,
        messages: List[ChatCompletionMessageParam],
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> AsyncGenerator[str, None]:
        """Stream completion chunks from OpenAI"""
        stream = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            n=1,
            stream=True,
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    async def generate_multiple(
        self,
        messages: List[ChatCompletionMessageParam],
        count: int = 3,
        model: str = "gpt-4o",
        temperature: float = 0.8,
        max_tokens: int = 100,
    ) -> List[str]:
        """
        Generate multiple completions in a single API call
        
        Args:
            messages: List of chat messages
            count: Number of completions to generate
            model: Model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens per completion
            
        Returns:
            List of generated texts
        """
        if not self.client:
            raise RuntimeError("OpenAI client not initialized")
        
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                n=count,
            )
            
            return [
                choice.message.content or ""
                for choice in response.choices
            ]
            
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {str(e)}") from e
    
    async def close(self):
        """Close the OpenAI client"""
        if self.client:
            await self.client.close()


# Create singleton instance but handle missing API key gracefully
try:
    llm_service = LLMService()
except ValueError:
    llm_service = None