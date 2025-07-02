from pydantic import BaseModel, Field
from typing import List, Literal
from enum import Enum


class GenerationMode(str, Enum):
    """Generation mode enum"""
    PICKUP = "pickup"
    REPLY = "reply"


class StylePreset(str, Enum):
    """Style preset enum"""
    SPICY = "spicy"
    SAFE = "safe"
    FUNNY = "funny"


class GenerateRequest(BaseModel):
    """Request model for /v1/generate endpoint"""
    mode: GenerationMode = Field(..., description="Generation mode: pickup or reply")
    style: StylePreset = Field(default=StylePreset.SAFE, description="Style preset")
    context: str = Field(..., min_length=1, max_length=1500, description="Input context text")
    
    class Config:
        json_schema_extra = {
            "example": {
                "mode": "pickup",
                "style": "safe",
                "context": "I love hiking and photography. Always looking for new adventures!"
            }
        }


class GenerateResponse(BaseModel):
    """Response model for /v1/generate endpoint"""
    choices: List[str] = Field(..., description="Generated text choices")
    style: StylePreset = Field(..., description="Style used for generation")
    mode: GenerationMode = Field(..., description="Generation mode used")
    
    class Config:
        json_schema_extra = {
            "example": {
                "choices": [
                    "I see you love adventures - what's the most spontaneous trip you've ever taken?",
                    "A fellow photographer! What's your favorite subject to capture?",
                    "Hiking enthusiast here too! What's your dream hiking destination?"
                ],
                "style": "safe",
                "mode": "pickup"
            }
        }


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    code: str = Field(..., description="Error code")
    details: dict = Field(default_factory=dict, description="Additional error details")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Content flagged by moderation system",
                "code": "CONTENT_UNSAFE",
                "details": {
                    "flagged_categories": ["harassment"],
                    "suggestion": "Please try with different content"
                }
            }
        }