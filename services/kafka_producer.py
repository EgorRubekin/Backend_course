import json
import asyncio
from aiokafka import AIOKafkaProducer
import logging

logger = logging.getLogger(__name__)

class KafkaProducerManager:
    def __init__(self):
        self.producer = None
        self.bootstrap_servers = "localhost:9092"

    async def start(self):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        await self.producer.start()

    async def stop(self):
        if self.producer:
            await self.producer.stop()

    async def send_moderation(self, item_id: int, task_id: int):
        payload = {
            "item_id": item_id,
            "task_id": task_id,
            "retry_count": 0
        }
        await self.producer.send_and_wait("moderation", payload)
        logger.info(f"Sent task {task_id} to Kafka")

kafka_producer = KafkaProducerManager()