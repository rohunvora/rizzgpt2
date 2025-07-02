from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import logging
from typing import Optional

from backend.services.quota_store import quota_store

logger = logging.getLogger(__name__)


class QuotaMiddleware(BaseHTTPMiddleware):
    """Middleware for enforcing rate limits based on device tokens"""
    
    def __init__(self, app, free_tier_limit: int = 5):
        super().__init__(app)
        self.free_tier_limit = free_tier_limit
        self.protected_paths = ["/v1/generate"]  # Paths that require quota checking
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request and enforce quota limits"""
        
        # Check if this path requires quota enforcement
        if not any(request.url.path.startswith(path) for path in self.protected_paths):
            return await call_next(request)
        
        # Extract device token from Authorization header
        device_token = self._extract_device_token(request)
        
        if not device_token:
            # For now, allow requests without device token (during development)
            # In production, this should return 401 Unauthorized
            logger.warning("Request without device token, allowing for development")
            return await call_next(request)
        
        try:
            # Check current quota
            can_proceed = await quota_store.can_use(device_token, self.free_tier_limit)
            
            if not can_proceed:
                # Get reset time for error response
                reset_time = await quota_store.get_reset_time(device_token)
                current_usage = await quota_store.get_usage(device_token)
                
                logger.info(f"Quota exceeded for device {device_token[:8]}... ({current_usage}/{self.free_tier_limit})")
                
                # Return 429 Too Many Requests
                raise HTTPException(
                    status_code=429,
                    detail={
                        "error": "Daily quota exceeded",
                        "code": "QUOTA_EXCEEDED",
                        "details": {
                            "current_usage": current_usage,
                            "daily_limit": self.free_tier_limit,
                            "reset_time": reset_time.isoformat() if reset_time else None,
                            "message": f"You have reached your daily limit of {self.free_tier_limit} requests. Please upgrade to premium or wait until midnight UTC for reset."
                        }
                    },
                    headers={
                        "X-RateLimit-Limit": str(self.free_tier_limit),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(int(reset_time.timestamp())) if reset_time else "",
                        "Retry-After": str(self._seconds_until_reset(reset_time)) if reset_time else "86400"
                    }
                )
            
            # Process the request
            response = await call_next(request)
            
            # If request was successful (2xx status), increment quota
            if 200 <= response.status_code < 300:
                new_usage = await quota_store.increment_usage(device_token)
                remaining = max(0, self.free_tier_limit - new_usage)
                
                # Add rate limit headers to response
                response.headers["X-RateLimit-Limit"] = str(self.free_tier_limit)
                response.headers["X-RateLimit-Remaining"] = str(remaining)
                
                reset_time = await quota_store.get_reset_time(device_token)
                if reset_time:
                    response.headers["X-RateLimit-Reset"] = str(int(reset_time.timestamp()))
                
                logger.debug(f"Request successful, device {device_token[:8]}... usage: {new_usage}/{self.free_tier_limit}")
            
            return response
            
        except HTTPException:
            # Re-raise HTTP exceptions (like quota exceeded)
            raise
        except Exception as e:
            logger.error(f"Error in quota middleware: {e}")
            # On error, allow the request to proceed (fail open)
            return await call_next(request)
    
    def _extract_device_token(self, request: Request) -> Optional[str]:
        """Extract device token from Authorization header"""
        auth_header = request.headers.get("Authorization")
        
        if not auth_header:
            return None
        
        if not auth_header.startswith("Bearer "):
            return None
        
        token = auth_header[7:]  # Remove "Bearer " prefix
        
        if not token or len(token) < 8:  # Minimum token length
            return None
        
        return token
    
    def _seconds_until_reset(self, reset_time) -> int:
        """Calculate seconds until quota reset"""
        if not reset_time:
            return 86400  # 24 hours default
        
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        delta = reset_time - now
        return max(0, int(delta.total_seconds()))


class QuotaManager:
    """Helper class for quota management operations"""
    
    def __init__(self, free_tier_limit: int = 5):
        self.free_tier_limit = free_tier_limit
    
    async def check_quota(self, device_token: str) -> dict:
        """
        Check quota status for a device token
        
        Returns:
            Dictionary with quota information
        """
        if not device_token:
            return {
                "can_use": True,
                "usage": 0,
                "limit": self.free_tier_limit,
                "remaining": self.free_tier_limit,
                "reset_time": None
            }
        
        usage = await quota_store.get_usage(device_token)
        can_use = await quota_store.can_use(device_token, self.free_tier_limit)
        reset_time = await quota_store.get_reset_time(device_token)
        
        return {
            "can_use": can_use,
            "usage": usage,
            "limit": self.free_tier_limit,
            "remaining": max(0, self.free_tier_limit - usage),
            "reset_time": reset_time.isoformat() if reset_time else None
        }
    
    async def increment_quota(self, device_token: str) -> int:
        """Increment quota and return new usage count"""
        if not device_token:
            return 0
        return await quota_store.increment_usage(device_token)
    
    async def reset_device_quota(self, device_token: str):
        """Reset quota for a specific device (admin operation)"""
        await quota_store.reset_quota(device_token)
    
    async def get_store_stats(self) -> dict:
        """Get quota store statistics"""
        return await quota_store.get_stats()


# Global quota manager instance
quota_manager = QuotaManager()