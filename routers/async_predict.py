from fastapi import APIRouter, HTTPException
from services.repositories import ad_repo
from services.kafka_producer import kafka_producer

router = APIRouter()

@router.post("/async_predict")
async def async_predict(item_id: int):
    ad = await ad_repo.get_ad_by_id(item_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")
    
    task_id = await ad_repo.create_moderation_task(item_id)
    
    await kafka_producer.send_moderation(item_id, task_id)
    
    return {"task_id": task_id, "status": "pending", "message": "Moderation request accepted"}

@router.get("/moderation_result/{task_id}")
async def get_moderation_result(task_id: int):
    task = await ad_repo.get_moderation_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {
        "task_id": task["id"],
        "status": task["status"],
        "is_violation": task["is_violation"],
        "probability": task["probability"]
    }