import json
import asyncio
import logging
import os 
from aiokafka import AIOKafkaProducer

logger = logging.getLogger(__name__)

class KafkaProducerManager:
    def __init__(self):
        self.producer = None
        self.bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

    async def start(self):
        for i in range(5):
            try:
                self.producer = AIOKafkaProducer(
                    bootstrap_servers=self.bootstrap_servers,
                    value_serializer=lambda v: json.dumps(v).encode('utf-8')
                )
                await self.producer.start()
                logger.info(f"Connected to Kafka at {self.bootstrap_servers}")
                break
            except Exception as e:
                logger.warning(f"Kafka connection attempt {i+1} failed: {e}")
                await asyncio.sleep(2)

    async def stop(self):
        if self.producer:
            try:
                await self.producer.stop()
                logger.info("Kafka producer stopped")
            except Exception as e:
                logger.error(f"Error while stopping Kafka producer: {e}")
        else:
            logger.warning("Kafka producer was not initialized, nothing to stop")

kafka_producer = KafkaProducerManager()