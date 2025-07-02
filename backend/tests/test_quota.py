import pytest
import asyncio
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

from backend.services.quota_store import QuotaStore, quota_store
from backend.middleware.quota import QuotaManager
from main import app

client = TestClient(app)


@pytest.fixture
async def clean_quota_store():
    """Fixture to provide a clean quota store for testing"""
    test_store = QuotaStore()
    yield test_store
    await test_store.shutdown()


@pytest.mark.asyncio
async def test_quota_store_basic_operations(clean_quota_store):
    """Test basic quota store operations"""
    store = clean_quota_store
    device_token = "test-device-123"
    
    # Initial usage should be 0
    usage = await store.get_usage(device_token)
    assert usage == 0
    
    # Should be able to use initially
    can_use = await store.can_use(device_token, 5)
    assert can_use is True
    
    # Increment usage
    new_usage = await store.increment_usage(device_token)
    assert new_usage == 1
    
    # Check usage again
    usage = await store.get_usage(device_token)
    assert usage == 1
    
    # Still under limit
    can_use = await store.can_use(device_token, 5)
    assert can_use is True


@pytest.mark.asyncio
async def test_quota_store_limit_enforcement(clean_quota_store):
    """Test quota limit enforcement"""
    store = clean_quota_store
    device_token = "test-device-456"
    limit = 3
    
    # Use up to limit
    for i in range(limit):
        can_use = await store.can_use(device_token, limit)
        assert can_use is True
        usage = await store.increment_usage(device_token)
        assert usage == i + 1
    
    # Should now be at limit
    can_use = await store.can_use(device_token, limit)
    assert can_use is False
    
    # Usage should be at limit
    usage = await store.get_usage(device_token)
    assert usage == limit


@pytest.mark.asyncio
async def test_quota_store_reset_functionality(clean_quota_store):
    """Test quota reset functionality"""
    store = clean_quota_store
    device_token = "test-device-789"
    
    # Use some quota
    await store.increment_usage(device_token)
    await store.increment_usage(device_token)
    usage = await store.get_usage(device_token)
    assert usage == 2
    
    # Manual reset
    await store.reset_quota(device_token)
    usage = await store.get_usage(device_token)
    assert usage == 0


@pytest.mark.asyncio
async def test_quota_store_midnight_reset():
    """Test UTC midnight reset logic"""
    store = QuotaStore()
    device_token = "test-device-midnight"
    
    # Mock the current time to be just before midnight
    with patch('backend.services.quota_store.datetime') as mock_datetime:
        # Set current time to 23:59 UTC
        mock_now = datetime(2024, 1, 1, 23, 59, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = mock_now
        mock_datetime.combine = datetime.combine
        
        # Use some quota
        await store.increment_usage(device_token)
        usage = await store.get_usage(device_token)
        assert usage == 1
        
        # Mock time after midnight
        mock_now_after = datetime(2024, 1, 2, 0, 1, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = mock_now_after
        
        # Usage should reset
        usage = await store.get_usage(device_token)
        assert usage == 0
    
    await store.shutdown()


@pytest.mark.asyncio
async def test_quota_store_stats(clean_quota_store):
    """Test quota store statistics"""
    store = clean_quota_store
    
    # Initial stats
    stats = await store.get_stats()
    assert stats['total_devices'] == 0
    assert stats['active_quotas'] == 0
    assert stats['total_usage_today'] == 0
    
    # Add some usage
    await store.increment_usage("device1")
    await store.increment_usage("device2")
    await store.increment_usage("device1")  # device1 has 2, device2 has 1
    
    stats = await store.get_stats()
    assert stats['total_devices'] == 2
    assert stats['active_quotas'] == 2
    assert stats['total_usage_today'] == 3


@pytest.mark.asyncio
async def test_quota_manager():
    """Test QuotaManager functionality"""
    manager = QuotaManager(free_tier_limit=3)
    device_token = "test-manager-device"
    
    # Mock the quota store
    with patch('backend.middleware.quota.quota_store') as mock_store:
        mock_store.get_usage = AsyncMock(return_value=1)
        mock_store.can_use = AsyncMock(return_value=True)
        mock_store.get_reset_time = AsyncMock(return_value=datetime.now(timezone.utc))
        
        quota_info = await manager.check_quota(device_token)
        
        assert quota_info['usage'] == 1
        assert quota_info['limit'] == 3
        assert quota_info['remaining'] == 2
        assert quota_info['can_use'] is True
        assert quota_info['reset_time'] is not None


def test_quota_middleware_without_token():
    """Test quota middleware with no authorization token"""
    # Should allow request without token (development mode)
    response = client.post("/v1/generate", json={
        "mode": "pickup",
        "style": "safe",
        "context": "Test content"
    })
    
    # Should not fail due to quota (might fail due to missing services)
    assert response.status_code in [200, 503]  # 503 if services not available


def test_quota_middleware_with_token():
    """Test quota middleware with authorization token"""
    headers = {"Authorization": "Bearer test-device-token-123"}
    
    response = client.post("/v1/generate", json={
        "mode": "pickup",
        "style": "safe",
        "context": "Test content"
    }, headers=headers)
    
    # Should not fail due to quota initially
    assert response.status_code in [200, 503]


@patch('backend.middleware.quota.quota_store')
def test_quota_middleware_quota_exceeded(mock_store):
    """Test quota middleware when quota is exceeded"""
    # Mock quota store to return quota exceeded
    mock_store.can_use = AsyncMock(return_value=False)
    mock_store.get_usage = AsyncMock(return_value=5)
    mock_store.get_reset_time = AsyncMock(return_value=datetime.now(timezone.utc) + timedelta(hours=1))
    
    headers = {"Authorization": "Bearer test-device-token-456"}
    
    response = client.post("/v1/generate", json={
        "mode": "pickup",
        "style": "safe",
        "context": "Test content"
    }, headers=headers)
    
    assert response.status_code == 429
    data = response.json()
    assert data["detail"]["code"] == "QUOTA_EXCEEDED"
    assert "X-RateLimit-Limit" in response.headers
    assert "X-RateLimit-Remaining" in response.headers


@patch('backend.middleware.quota.quota_store')
def test_quota_middleware_successful_request(mock_store):
    """Test quota middleware with successful request"""
    # Mock quota store
    mock_store.can_use = AsyncMock(return_value=True)
    mock_store.increment_usage = AsyncMock(return_value=2)
    mock_store.get_reset_time = AsyncMock(return_value=datetime.now(timezone.utc) + timedelta(hours=1))
    
    # Mock the services to make request successful
    with patch('backend.routers.generate.moderation_service') as mock_moderation, \
         patch('backend.routers.generate.llm_service') as mock_llm:
        
        mock_moderation.moderate_content = AsyncMock(return_value=(True, {"overall_safe": True}))
        mock_llm.generate_multiple = AsyncMock(return_value=["Response 1", "Response 2", "Response 3"])
        
        headers = {"Authorization": "Bearer test-device-token-789"}
        
        response = client.post("/v1/generate", json={
            "mode": "pickup",
            "style": "safe",
            "context": "Test content"
        }, headers=headers)
        
        assert response.status_code == 200
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
        assert response.headers["X-RateLimit-Limit"] == "5"
        assert response.headers["X-RateLimit-Remaining"] == "3"  # 5 - 2 = 3


def test_quota_middleware_non_protected_path():
    """Test that quota middleware doesn't affect non-protected paths"""
    # Health check should not be affected by quota
    response = client.get("/health")
    assert response.status_code == 200
    
    # Root endpoint should not be affected
    response = client.get("/")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_quota_store_empty_token():
    """Test quota store with empty/None device token"""
    store = QuotaStore()
    
    # Empty token should return 0 usage
    usage = await store.get_usage("")
    assert usage == 0
    
    usage = await store.get_usage(None)
    assert usage == 0
    
    # Should not increment for empty token
    new_usage = await store.increment_usage("")
    assert new_usage == 0
    
    await store.shutdown()


@pytest.mark.asyncio
async def test_quota_store_concurrent_access():
    """Test quota store under concurrent access"""
    store = QuotaStore()
    device_token = "concurrent-test-device"
    
    async def increment_quota():
        return await store.increment_usage(device_token)
    
    # Run multiple increments concurrently
    tasks = [increment_quota() for _ in range(10)]
    results = await asyncio.gather(*tasks)
    
    # Results should be sequential (1, 2, 3, ..., 10)
    assert sorted(results) == list(range(1, 11))
    
    # Final usage should be 10
    final_usage = await store.get_usage(device_token)
    assert final_usage == 10
    
    await store.shutdown()