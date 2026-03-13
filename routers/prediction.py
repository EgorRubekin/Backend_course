from fastapi import APIRouter, HTTPException, status, Depends 
from models.prediction import AdItem, PredictionResponse
from services.prediction import prediction_service
from routers.auth import get_current_account
from models.account import AccountModel

router = APIRouter()

@router.post("/predict", response_model=PredictionResponse)
async def predict(
    item: AdItem, 
    current_account: AccountModel = Depends(get_current_account)
):
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