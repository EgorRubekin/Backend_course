from fastapi import APIRouter, Depends, HTTPException
from repositories.ad_repo import ad_repo 
from services.cache import cache_storage

router = APIRouter()

@router.post("/close/{item_id}")
async def close_ad(item_id: int):
    result = await ad_repo.delete_ad_full(item_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="Объявление не найдено")

    await cache_storage.delete(item_id)
    
    return {"status": "closed", "item_id": item_id}