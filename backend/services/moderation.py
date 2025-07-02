import re
import asyncio
from typing import Dict, List, Optional, Tuple, Union
from openai import AsyncOpenAI
from backend.config import settings
import os


class ModerationService:
    """Content moderation service using OpenAI Moderation API and custom filters"""
    
    # Safety score thresholds
    HARASSMENT_THRESHOLD = 0.9
    SEXUAL_THRESHOLD = 0.9
    VIOLENCE_THRESHOLD = 0.95
    
    # Regex patterns for filtering
    PHONE_PATTERN = re.compile(
        r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
    )
    ADDRESS_PATTERN = re.compile(
        r'\d+\s+[A-Za-z0-9\s,]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd)\b',
        re.IGNORECASE
    )
    EMAIL_PATTERN = re.compile(
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    )
    
    # Blocked terms (basic list - would be expanded with database)
    BLOCKED_TERMS = [
        "underage", "minor", "child", "kid", "teen", "school",
        "rape", "assault", "abuse", "violence", "harm",
        "suicide", "self-harm", "cutting", "drugs", "cocaine"
    ]
    
    def __init__(self):
        self.client = None
        try:
            self._initialize_client()
        except ValueError:
            # Allow initialization without API key for testing
            pass
    
    def _initialize_client(self):
        """Initialize OpenAI client for moderation"""
        api_key = settings.openai_api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key not found for moderation service")
        
        self.client = AsyncOpenAI(api_key=api_key)
    
    async def moderate_content(self, text: str) -> Tuple[bool, Dict]:
        """
        Moderate content using OpenAI Moderation API and custom filters
        
        Args:
            text: Text content to moderate
            
        Returns:
            Tuple of (is_safe, moderation_details)
        """
        if not text or not text.strip():
            return True, {"reason": "empty_content"}
        
        # Run all moderation checks in parallel
        results = await asyncio.gather(
            self._openai_moderation(text),
            self._regex_filters(text),
            self._blocklist_check(text),
            return_exceptions=True
        )
        
        # Handle exceptions and extract results
        openai_result = results[0] if not isinstance(results[0], Exception) else (True, {"error": str(results[0])})
        regex_result = results[1] if not isinstance(results[1], Exception) else (True, {"error": str(results[1])})
        blocklist_result = results[2] if not isinstance(results[2], Exception) else (True, {"error": str(results[2])})
        
        # Combine results - content is safe only if all checks pass
        is_safe = all([
            openai_result[0],
            regex_result[0], 
            blocklist_result[0]
        ])
        
        details = {
            "openai": openai_result[1],
            "regex": regex_result[1],
            "blocklist": blocklist_result[1],
            "overall_safe": is_safe
        }
        
        return is_safe, details
    
    async def _openai_moderation(self, text: str) -> Tuple[bool, Dict]:
        """Check content using OpenAI Moderation API"""
        if not self.client:
            return True, {"error": "moderation_client_not_initialized"}
        
        try:
            response = await self.client.moderations.create(input=text)
            result = response.results[0]
            
            # Check specific categories against thresholds
            flagged_categories = []
            scores = result.category_scores
            
            if scores.harassment > self.HARASSMENT_THRESHOLD:
                flagged_categories.append("harassment")
            if scores.sexual > self.SEXUAL_THRESHOLD:
                flagged_categories.append("sexual")
            if scores.violence > self.VIOLENCE_THRESHOLD:
                flagged_categories.append("violence")
            
            is_safe = len(flagged_categories) == 0
            
            return is_safe, {
                "flagged": result.flagged,
                "flagged_categories": flagged_categories,
                "scores": {
                    "harassment": float(scores.harassment),
                    "sexual": float(scores.sexual),
                    "violence": float(scores.violence),
                    "hate": float(scores.hate),
                }
            }
            
        except Exception as e:
            # On API error, be conservative and allow content
            return True, {"error": f"moderation_api_error: {str(e)}"}
    
    async def _regex_filters(self, text: str) -> Tuple[bool, Dict]:
        """Check for personal information using regex patterns"""
        violations = []
        
        # Check for phone numbers
        if self.PHONE_PATTERN.search(text):
            violations.append("phone_number")
        
        # Check for addresses
        if self.ADDRESS_PATTERN.search(text):
            violations.append("address")
        
        # Check for email addresses
        if self.EMAIL_PATTERN.search(text):
            violations.append("email")
        
        is_safe = len(violations) == 0
        
        return is_safe, {
            "violations": violations,
            "patterns_checked": ["phone", "address", "email"]
        }
    
    async def _blocklist_check(self, text: str) -> Tuple[bool, Dict]:
        """Check against blocked terms list"""
        text_lower = text.lower()
        found_terms = []
        
        for term in self.BLOCKED_TERMS:
            if term in text_lower:
                found_terms.append(term)
        
        is_safe = len(found_terms) == 0
        
        return is_safe, {
            "blocked_terms_found": found_terms,
            "total_blocked_terms": len(self.BLOCKED_TERMS)
        }
    
    def add_blocked_term(self, term: str):
        """Add a term to the blocklist"""
        if term.lower() not in [t.lower() for t in self.BLOCKED_TERMS]:
            self.BLOCKED_TERMS.append(term.lower())
    
    def remove_blocked_term(self, term: str):
        """Remove a term from the blocklist"""
        self.BLOCKED_TERMS = [t for t in self.BLOCKED_TERMS if t.lower() != term.lower()]
    
    async def close(self):
        """Close the OpenAI client"""
        if self.client:
            await self.client.close()


# Create singleton instance
try:
    moderation_service = ModerationService()
except ValueError:
    moderation_service = None