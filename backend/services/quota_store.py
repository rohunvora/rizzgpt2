import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class QuotaStore:
    """In-memory quota tracking with UTC midnight reset"""
    
    def __init__(self):
        self._quotas: Dict[str, Dict] = {}  # device_token -> {count, reset_time}
        self._lock = asyncio.Lock()
        self._cleanup_task: Optional[asyncio.Task] = None
        self._start_cleanup_task()
    
    def _start_cleanup_task(self):
        """Start background task for quota cleanup"""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_expired_quotas())
    
    async def _cleanup_expired_quotas(self):
        """Background task to clean up expired quota entries"""
        while True:
            try:
                await asyncio.sleep(3600)  # Check every hour
                async with self._lock:
                    current_time = datetime.now(timezone.utc)
                    expired_tokens = [
                        token for token, data in self._quotas.items()
                        if current_time >= data['reset_time']
                    ]
                    
                    for token in expired_tokens:
                        del self._quotas[token]
                    
                    if expired_tokens:
                        logger.info(f"Cleaned up {len(expired_tokens)} expired quota entries")
                        
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in quota cleanup task: {e}")
    
    def _get_next_midnight_utc(self) -> datetime:
        """Get the next UTC midnight timestamp"""
        now = datetime.now(timezone.utc)
        # Get tomorrow at midnight UTC
        tomorrow = now.date() + timedelta(days=1)
        midnight = datetime.combine(tomorrow, datetime.min.time(), timezone.utc)
        return midnight
    
    async def get_usage(self, device_token: str) -> int:
        """
        Get current usage count for a device token
        
        Args:
            device_token: Unique device identifier
            
        Returns:
            Current usage count for today
        """
        if not device_token:
            return 0
            
        async with self._lock:
            current_time = datetime.now(timezone.utc)
            
            if device_token not in self._quotas:
                return 0
            
            quota_data = self._quotas[device_token]
            
            # Check if quota has expired (past midnight UTC)
            if current_time >= quota_data['reset_time']:
                # Reset the quota
                self._quotas[device_token] = {
                    'count': 0,
                    'reset_time': self._get_next_midnight_utc()
                }
                return 0
            
            return quota_data['count']
    
    async def increment_usage(self, device_token: str) -> int:
        """
        Increment usage count for a device token
        
        Args:
            device_token: Unique device identifier
            
        Returns:
            New usage count after increment
        """
        if not device_token:
            return 0
            
        async with self._lock:
            current_time = datetime.now(timezone.utc)
            
            if device_token not in self._quotas:
                # Initialize new quota entry
                self._quotas[device_token] = {
                    'count': 0,
                    'reset_time': self._get_next_midnight_utc()
                }
            
            quota_data = self._quotas[device_token]
            
            # Check if quota has expired (past midnight UTC)
            if current_time >= quota_data['reset_time']:
                # Reset the quota
                quota_data['count'] = 0
                quota_data['reset_time'] = self._get_next_midnight_utc()
            
            # Increment count
            quota_data['count'] += 1
            
            logger.debug(f"Device {device_token[:8]}... usage: {quota_data['count']}")
            
            return quota_data['count']
    
    async def can_use(self, device_token: str, limit: int) -> bool:
        """
        Check if device token can make another request without exceeding limit
        
        Args:
            device_token: Unique device identifier
            limit: Maximum allowed requests per day
            
        Returns:
            True if under limit, False if at or over limit
        """
        current_usage = await self.get_usage(device_token)
        return current_usage < limit
    
    async def get_reset_time(self, device_token: str) -> Optional[datetime]:
        """
        Get the reset time for a device token's quota
        
        Args:
            device_token: Unique device identifier
            
        Returns:
            Reset time as UTC datetime, or None if no quota exists
        """
        if not device_token:
            return None
            
        async with self._lock:
            if device_token not in self._quotas:
                return self._get_next_midnight_utc()
            
            return self._quotas[device_token]['reset_time']
    
    async def reset_quota(self, device_token: str):
        """
        Manually reset quota for a device token (for testing/admin purposes)
        
        Args:
            device_token: Unique device identifier
        """
        if not device_token:
            return
            
        async with self._lock:
            if device_token in self._quotas:
                self._quotas[device_token] = {
                    'count': 0,
                    'reset_time': self._get_next_midnight_utc()
                }
                logger.info(f"Manually reset quota for device {device_token[:8]}...")
    
    async def get_stats(self) -> Dict:
        """
        Get quota store statistics
        
        Returns:
            Dictionary with store statistics
        """
        async with self._lock:
            current_time = datetime.now(timezone.utc)
            active_quotas = 0
            total_usage = 0
            
            for quota_data in self._quotas.values():
                if current_time < quota_data['reset_time']:
                    active_quotas += 1
                    total_usage += quota_data['count']
            
            return {
                'total_devices': len(self._quotas),
                'active_quotas': active_quotas,
                'total_usage_today': total_usage,
                'cleanup_task_running': not (self._cleanup_task is None or self._cleanup_task.done())
            }
    
    async def shutdown(self):
        """Cleanup resources"""
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass


# Global quota store instance
quota_store = QuotaStore()