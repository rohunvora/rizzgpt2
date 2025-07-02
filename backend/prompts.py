from typing import List, Dict
from backend.schemas import GenerationMode, StylePreset


class PromptTemplates:
    """Centralized prompt templates for different generation modes and styles"""
    
    # Base system prompts
    PICKUP_SYSTEM_BASE = """You are a witty but respectful dating assistant. Your goal is to help users create engaging conversation starters based on someone's dating profile bio."""
    
    REPLY_SYSTEM_BASE = """You are helping someone continue a dating conversation. Match their tone and energy while keeping the conversation flowing naturally."""
    
    # Style modifiers
    STYLE_MODIFIERS = {
        StylePreset.SAFE: {
            "tone": "friendly, respectful, and genuine",
            "approach": "Focus on shared interests and asking thoughtful questions",
            "avoid": "anything that could be seen as inappropriate or overly forward"
        },
        StylePreset.SPICY: {
            "tone": "confident, playful, and slightly flirtatious",
            "approach": "Use subtle humor and light teasing while remaining respectful",
            "avoid": "anything explicit, crude, or disrespectful"
        },
        StylePreset.FUNNY: {
            "tone": "humorous, lighthearted, and entertaining",
            "approach": "Use clever wordplay, puns, or situational humor",
            "avoid": "offensive jokes or humor at someone's expense"
        }
    }
    
    @classmethod
    def get_pickup_prompt(cls, bio: str, style: StylePreset) -> List[Dict[str, str]]:
        """Generate pickup line prompt based on bio and style"""
        style_info = cls.STYLE_MODIFIERS[style]
        
        system_prompt = f"""{cls.PICKUP_SYSTEM_BASE}

STYLE: {style_info['tone']}
APPROACH: {style_info['approach']}
IMPORTANT: {style_info['avoid']}

INSTRUCTIONS:
1. Read the person's bio carefully
2. Identify 2-3 key interests or personality traits
3. Create three distinct conversation starters that reference their bio
4. Each should be 15-30 words maximum
5. Make them engaging questions or observations that invite a response
6. Ensure they feel personalized, not generic

OUTPUT FORMAT: Return exactly 3 lines, each on a new line, no numbering or bullets."""
        
        user_prompt = f"""USER'S BIO: "{bio}"

Generate 3 personalized conversation starters based on this bio."""
        
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    
    @classmethod
    def get_reply_prompt(cls, chat_history: str, style: StylePreset) -> List[Dict[str, str]]:
        """Generate reply prompt based on chat history and style"""
        style_info = cls.STYLE_MODIFIERS[style]
        
        system_prompt = f"""{cls.REPLY_SYSTEM_BASE}

STYLE: {style_info['tone']}
APPROACH: {style_info['approach']}
IMPORTANT: {style_info['avoid']}

INSTRUCTIONS:
1. Analyze the conversation flow and tone
2. Understand what the other person just said
3. Generate 2 different response options that:
   - Acknowledge their message
   - Keep the conversation going
   - Match the established tone
   - Ask a follow-up question or share something relevant
4. Each response should be 10-25 words
5. Make them feel natural and conversational

OUTPUT FORMAT: Return exactly 2 lines, each on a new line, no numbering or bullets."""
        
        user_prompt = f"""RECENT CHAT MESSAGES:
{chat_history}

Generate 2 natural response options to continue this conversation."""
        
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    
    @classmethod
    def get_expected_count(cls, mode: GenerationMode) -> int:
        """Get expected number of responses for each mode"""
        return {
            GenerationMode.PICKUP: 3,
            GenerationMode.REPLY: 2
        }[mode]
    
    @classmethod
    def get_max_tokens(cls, mode: GenerationMode) -> int:
        """Get max tokens for each mode"""
        return {
            GenerationMode.PICKUP: 100,  # ~30 words * 3 = 90 words + buffer
            GenerationMode.REPLY: 70     # ~25 words * 2 = 50 words + buffer
        }[mode]
    
    @classmethod
    def get_temperature(cls, style: StylePreset) -> float:
        """Get temperature setting for each style"""
        return {
            StylePreset.SAFE: 0.7,      # More conservative
            StylePreset.SPICY: 0.8,     # More creative
            StylePreset.FUNNY: 0.9      # Most creative
        }[style]