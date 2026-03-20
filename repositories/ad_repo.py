import time
from db import db
from models.prediction import PredictionRequest
from app.metrics import DB_QUERY_DURATION

class AdRepository:
    async def get_ad_by_id(self, item_id: int):
        start_time = time.time()
        try:
            query = """
            SELECT ads.id as item_id, ads.seller_id, account.is_verified_seller,
                   ads.title as name, ads.description, ads.category_id as category, ads.images_qty
            FROM ads
            JOIN account ON ads.seller_id = account.id
            WHERE ads.id = $1
            """
            row = await db.pool.fetchrow(query, item_id)
            return PredictionRequest(**dict(row)) if row else None
        finally:
            duration = time.time() - start_time
            DB_QUERY_DURATION.labels(query_type="select_join").observe(duration)

    async def update_moderation_task(self, task_id: int, status: str, 
                                     is_violation: bool = None, 
                                     probability: float = None, 
                                     error_message: str = None):
        query = """
        UPDATE moderation_results 
        SET status = $2, is_violation = $3, probability = $4, 
            error_message = $5, processed_at = NOW()
        WHERE id = $1
        """
        await db.pool.execute(query, task_id, status, is_violation, probability, error_message)

    async def delete_ad_full(self, item_id: int):
        async with db.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute("DELETE FROM moderation_results WHERE item_id = $1", item_id)
                return await conn.execute("DELETE FROM ads WHERE id = $1", item_id)
            
    async def create_moderation_task(self, item_id: int) -> int:
        query = """
        INSERT INTO moderation_results (item_id, status)
        VALUES ($1, 'pending') RETURNING id
        """
        return await db.pool.fetchval(query, item_id)

    async def get_moderation_task(self, task_id: int):
        query = "SELECT * FROM moderation_results WHERE id = $1"
        row = await db.pool.fetchrow(query, task_id)
        return dict(row) if row else None

ad_repo = AdRepository()