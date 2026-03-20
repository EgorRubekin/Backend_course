from fastapi import APIRouter, HTTPException, status, Depends 
from models.prediction import PredictionRequest, PredictionResponse
from services.prediction import prediction_service
from services.cache import cache_storage
from services.kafka_producer import kafka_producer
from repositories.ad_repo import ad_repo  
from routers.auth import get_current_account
from models.account import AccountModel

router = APIRouter()

@router.post("/predict", response_model=PredictionResponse, tags=["ML"])
async def predict(
    item: PredictionRequest,  
    current_account: AccountModel = Depends(get_current_account)
):
    try:
        return prediction_service.predict(item)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/simple_predict/{item_id}", response_model=PredictionResponse, tags=["ML"])
async def simple_predict(
    item_id: int, 
    current_account: AccountModel = Depends(get_current_account)
):
    cached = await cache_storage.get(item_id)
    if cached:
        return cached

    item = await ad_repo.get_ad_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Объявление не найдено")

    result = prediction_service.predict(item)
    
    await cache_storage.set(item_id, result)
    return result

@router.post("/async_predict/{item_id}", tags=["ML"])
async def async_predict(
    item_id: int, 
    current_account: AccountModel = Depends(get_current_account)
):
    task_id = await ad_repo.create_moderation_task(item_id)
    
    await kafka_producer.send_moderation(item_id, task_id)
    
    return {"task_id": task_id, "status": "pending"}

@router.get("/moderation_result/{task_id}", tags=["ML"])
async def get_moderation_result(
    task_id: int, 
    current_account: AccountModel = Depends(get_current_account)
):
    result = await ad_repo.get_moderation_task(task_id)
    if not result:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    
    return result