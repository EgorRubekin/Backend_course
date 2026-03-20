from fastapi import APIRouter, HTTPException, Depends
from app.metrics import PREDICTIONS_TOTAL 
from services.repositories import ad_repo
from services.prediction import prediction_service
from models.prediction import PredictionRequest
from routers.auth import get_current_account
from models.account import AccountModel
from services.cache import cache_storage

router = APIRouter()

@router.post("/create_item", tags=["Ads Management"])
async def create_item(
    item: PredictionRequest,
    current_account: AccountModel = Depends(get_current_account)
):
    new_id = await ad_repo.create_ad(
        seller_id=item.seller_id,
        title=item.name,
        description=item.description,
        category=item.category,
        img_qty=item.images_qty
    )
    return {"status": "created", "item_id": new_id}

@router.get("/simple_predict")
async def simple_predict(
    item_id: int,
    current_account: AccountModel = Depends(get_current_account)
):
    cached_result = await cache_storage.get(item_id)
    if cached_result:
        return cached_result

    item_data = await ad_repo.get_ad_by_id(item_id)
    if item_data is None:
        raise HTTPException(status_code=404, detail="Item not found in database")
    
    result = prediction_service.predict(item_data)
    
    await cache_storage.set(item_id, result)
    
    return result