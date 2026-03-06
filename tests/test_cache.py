import pytest
from unittest.mock import AsyncMock, patch
from routers.simple_predict import simple_predict
from services.cache import cache_storage

@pytest.mark.asyncio
async def test_simple_predict_returns_cached_value():
    with patch("routers.simple_predict.cache_storage", new_callable=AsyncMock) as mock_cache:
        mock_cache.get.return_value = {"is_violation": False, "probability": 0.1}
        
        result = await simple_predict(item_id=1)
        
        mock_cache.get.assert_called_once_with(1)
        assert result["is_violation"] is False
        assert result["probability"] == 0.1


@pytest.mark.integration
@pytest.mark.asyncio
async def test_redis_set_get_integration():
    test_id = 12345
    data = {"is_violation": True, "probability": 0.9}
    
    await cache_storage.set(test_id, data)
    
    res = await cache_storage.get(test_id)
    
    assert res is not None
    assert res.is_violation == True
    assert res.probability == 0.9
    
    await cache_storage.delete(test_id)