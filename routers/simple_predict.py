from fastapi import APIRouter, HTTPException, Depends
from app.metrics import PREDICTIONS_TOTAL 
from services.repositories import ad_repo
from services.prediction import prediction_service
from models.prediction import AdItem 
from routers.auth import get_current_account
from models.account import AccountModel

router = APIRouter()

@router.post("/create_item", tags=["Ads Management"])
async def create_item(
    item: AdItem,
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
    result = await prediction_service.predict_by_id(item_id)
    
    if result is None:
        raise HTTPException(status_code=404, detail="Item not found in database")
    
    return result