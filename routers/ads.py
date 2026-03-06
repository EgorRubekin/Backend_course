from fastapi import APIRouter
from services.repositories import ad_repo
from services.cache import cache_storage

# Создаем объект роутера, который мы потом подключим в main.py
router = APIRouter()

@router.post("/close")
async def close_ad(item_id: int):
    # 1. Удаляем из PostgreSQL (через репозиторий)
    await ad_repo.delete_ad_full(item_id)
    
    # 2. Удаляем из Redis (инвалидация кэша)
    await cache_storage.delete(item_id)
    
    return {
        "status": "ok", 
        "message": f"Ad {item_id} removed from DB and Cache"
    }