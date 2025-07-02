from fastapi import APIRouter, HTTPException, Header
from typing import Optional
import logging

from backend.schemas import GenerateRequest, GenerateResponse, ErrorResponse, GenerationMode
from backend.services.moderation import moderation_service
from backend.services.llm import llm_service
from backend.prompts import PromptTemplates

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1", tags=["generation"])


@router.post("/generate", response_model=GenerateResponse)
async def generate_content(
    request: GenerateRequest,
    authorization: Optional[str] = Header(None, description="Bearer token for device authentication")
) -> GenerateResponse:
    """
    Generate pickup lines or conversation replies based on input context
    
    Args:
        request: Generation request containing mode, style, and context
        authorization: Bearer token for device authentication (future use)
    
    Returns:
        Generated text choices
        
    Raises:
        HTTPException: For various error conditions
    """
    try:
        # Extract device token from authorization header (for future quota tracking)
        device_token = None
        if authorization and authorization.startswith("Bearer "):
            device_token = authorization[7:]
        
        logger.info(f"Generation request: mode={request.mode}, style={request.style}, context_length={len(request.context)}")
        
        # Step 1: Content moderation
        if not moderation_service:
            logger.warning("Moderation service not available, proceeding without moderation")
        else:
            is_safe, moderation_details = await moderation_service.moderate_content(request.context)
            
            if not is_safe:
                logger.warning(f"Content flagged by moderation: {moderation_details}")
                
                # Determine specific error details
                error_details = {"moderation_results": moderation_details}
                flagged_categories = []
                
                if "openai" in moderation_details and "flagged_categories" in moderation_details["openai"]:
                    flagged_categories.extend(moderation_details["openai"]["flagged_categories"])
                
                if "regex" in moderation_details and moderation_details["regex"].get("violations"):
                    flagged_categories.extend(moderation_details["regex"]["violations"])
                
                if "blocklist" in moderation_details and moderation_details["blocklist"].get("blocked_terms_found"):
                    flagged_categories.extend(moderation_details["blocklist"]["blocked_terms_found"])
                
                error_details["flagged_categories"] = flagged_categories
                error_details["suggestion"] = "Please try with different content that follows our community guidelines"
                
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "Content flagged by moderation system",
                        "code": "CONTENT_UNSAFE",
                        "details": error_details
                    }
                )
        
        # Step 2: Generate prompt based on mode and style
        if request.mode == GenerationMode.PICKUP:
            messages = PromptTemplates.get_pickup_prompt(request.context, request.style)
        elif request.mode == GenerationMode.REPLY:
            messages = PromptTemplates.get_reply_prompt(request.context, request.style)
        else:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid generation mode",
                    "code": "INVALID_MODE",
                    "details": {"supported_modes": ["pickup", "reply"]}
                }
            )
        
        # Step 3: Generate content using LLM
        if not llm_service:
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "LLM service not available",
                    "code": "SERVICE_UNAVAILABLE",
                    "details": {"message": "AI service is temporarily unavailable"}
                }
            )
        
        # Get generation parameters
        expected_count = PromptTemplates.get_expected_count(request.mode)
        max_tokens = PromptTemplates.get_max_tokens(request.mode)
        temperature = PromptTemplates.get_temperature(request.style)
        
        try:
            # Generate multiple completions
            generated_texts = await llm_service.generate_multiple(
                messages=messages,
                count=expected_count,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Clean up generated text (remove empty lines, strip whitespace)
            choices = []
            for text in generated_texts:
                if text and text.strip():
                    # Split by newlines and take non-empty lines
                    lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
                    choices.extend(lines)
            
            # Ensure we have the expected number of choices
            if len(choices) < expected_count:
                logger.warning(f"Generated fewer choices than expected: {len(choices)} < {expected_count}")
                # Pad with generic fallbacks if needed
                while len(choices) < expected_count:
                    if request.mode == GenerationMode.PICKUP:
                        choices.append("I'd love to know more about you!")
                    else:
                        choices.append("That's interesting! Tell me more.")
            
            # Limit to expected count
            choices = choices[:expected_count]
            
            # Step 4: Moderate generated content
            if moderation_service:
                moderated_choices = []
                for choice in choices:
                    is_safe, _ = await moderation_service.moderate_content(choice)
                    if is_safe:
                        moderated_choices.append(choice)
                    else:
                        logger.warning(f"Generated content flagged: {choice}")
                        # Replace with safe fallback
                        if request.mode == GenerationMode.PICKUP:
                            moderated_choices.append("I'd love to get to know you better!")
                        else:
                            moderated_choices.append("That sounds great!")
                
                choices = moderated_choices
            
            logger.info(f"Successfully generated {len(choices)} choices")
            
            return GenerateResponse(
                choices=choices,
                style=request.style,
                mode=request.mode
            )
            
        except Exception as llm_error:
            logger.error(f"LLM generation error: {str(llm_error)}")
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "Failed to generate content",
                    "code": "GENERATION_FAILED",
                    "details": {"message": "AI service encountered an error"}
                }
            )
    
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error in generate_content: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "code": "INTERNAL_ERROR",
                "details": {"message": "An unexpected error occurred"}
            }
        )