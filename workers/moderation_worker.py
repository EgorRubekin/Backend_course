import asyncio
import json
import logging
import datetime
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from db import db
from services.repositories import ad_repo
from services.prediction import prediction_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Worker")

MAX_RETRIES = 3
RETRY_DELAY = 5  # секунд перед повтором

async def run_worker():
    await db.connect()
    prediction_service.startup()
    
    consumer = AIOKafkaConsumer(
        "moderation",
        bootstrap_servers="localhost:9092",
        group_id="moderation_group",
        value_deserializer=lambda v: json.loads(v.decode('utf-8'))
    )
    
    producer = AIOKafkaProducer(
        bootstrap_servers="localhost:9092",
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    await consumer.start()
    await producer.start()
    
    logger.info("Worker стартанул")

    try:
        async for msg in consumer:
            data = msg.value
            task_id = data.get("task_id")
            item_id = data.get("item_id")
            retry_count = data.get("retry_count", 0)
            
            logger.info(f"Обработка задачи {task_id} (попытка {retry_count + 1})")

            try:
                ad_item = await ad_repo.get_ad_by_id(item_id)
                if not ad_item:
                    raise ValueError(f"Объявление {item_id} не найдено в базе")
                
                result = prediction_service.predict(ad_item)
                
                await ad_repo.update_moderation_task(
                    task_id, "completed", 
                    is_violation=result["is_violation"], 
                    probability=result["probability"]
                )
                logger.info(f"Задача {task_id} успешно выполнена")

            except Exception as e:
                error_msg = str(e)
                logger.warning(f"Ошибка при обработке задачи {task_id}: {error_msg}")

                if retry_count < MAX_RETRIES:
                    logger.info(f"Ждем {RETRY_DELAY} сек и пробуем снова ({retry_count + 1}/{MAX_RETRIES})")
                    await asyncio.sleep(RETRY_DELAY)
                    
                    data["retry_count"] = retry_count + 1
                    await producer.send_and_wait("moderation", data)
                else:
                    # DLQ 
                    logger.error(f"Лимит попыток исчерпан для задачи {task_id}. Отправка в DLQ.")
                    
                    await ad_repo.update_moderation_task(task_id, "failed", error_message=error_msg)
                    
                    dlq_payload = {
                        "original_message": data,
                        "error": error_msg,
                        "timestamp": datetime.datetime.utcnow().isoformat(),
                        "final_retry_count": retry_count
                    }
                    await producer.send_and_wait("moderation_dlq", dlq_payload)

    finally:
        await consumer.stop()
        await producer.stop()
        await db.disconnect()

if __name__ == "__main__":
    asyncio.run(run_worker())