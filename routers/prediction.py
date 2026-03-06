from fastapi import APIRouter, HTTPException, status
from models.prediction import AdItem, PredictionResponse
from services.prediction import prediction_service

router = APIRouter()

@router.post("/predict", response_model=PredictionResponse)
async def predict(item: AdItem):
    try:
        result = prediction_service.predict(item)
        return result
    
    except RuntimeError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ML model is not available"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal prediction error: {str(e)}"
        )