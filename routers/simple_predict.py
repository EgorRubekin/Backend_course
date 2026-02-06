from fastapi import APIRouter, HTTPException
from models.prediction import PredictionResponse
from services.prediction import prediction_service

router = APIRouter()

@router.get("/simple_predict", response_model=PredictionResponse)
async def simple_predict(item_id: int):
    result = await prediction_service.predict_by_id(item_id)
    
    if result is None:
        raise HTTPException(status_code=404, detail="Объявление не найдено в базе данных")
        
    return result