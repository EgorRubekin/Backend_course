import json
import redis.asyncio as redis
from models.prediction import PredictionResponse

class PredictionCache:
    def __init__(self, host="localhost", port=6379):
        self.client = redis.Redis(host=host, port=port, decode_responses=True)
        self.ttl = 3600

    async def get(self, item_id: int) -> PredictionResponse | None:
        key = f"prediction:{item_id}"
        data = await self.client.get(key)
        if data:
            return PredictionResponse(**json.loads(data))
        return None

    async def set(self, item_id: int, prediction: dict):
        key = f"prediction:{item_id}"
        await self.client.set(key, json.dumps(prediction), ex=self.ttl)

    async def delete(self, item_id: int):
        await self.client.delete(f"prediction:{item_id}")

cache_storage = PredictionCache()