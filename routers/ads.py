from fastapi import APIRouter
from services.repositories import ad_repo
from services.cache import cache_storage

router = APIRouter()

@router.post("/close")
async def close_ad(item_id: int):
    await ad_repo.delete_ad_full(item_id)
    
    await cache_storage.delete(item_id)
    
    return {
        "status": "ok", 
        "message": f"Ad {item_id} removed from DB and Cache"
    }

