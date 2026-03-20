import json
import os
import redis.asyncio as redis
from models.prediction import PredictionResponse

class PredictionCache:
    def __init__(self):
        self.host = os.getenv("REDIS_HOST", "localhost")
        self.port = int(os.getenv("REDIS_PORT", 6379))
        self.client = redis.Redis(
            host=self.host, 
            port=self.port, 
            decode_responses=True
        )
        self.ttl = 3600

    async def get(self, item_id: int) -> PredictionResponse | None:
        key = f"prediction:{item_id}"
        try:
            data = await self.client.get(key)
            if data:
                return PredictionResponse(**json.loads(data))
        except Exception:
            return None
        return None

    async def set(self, item_id: int, prediction: dict):
        key = f"prediction:{item_id}"
        try:
            await self.client.set(key, json.dumps(prediction), ex=self.ttl)
        except Exception:
            pass

    async def delete(self, item_id: int):
        try:
            await self.client.delete(f"prediction:{item_id}")
        except Exception:
            pass

cache_storage = PredictionCache()