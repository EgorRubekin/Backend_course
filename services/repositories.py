import time
from db import db
from models.prediction import AdItem
from app.metrics import DB_QUERY_DURATION

class AdRepository:

    async def get_ad_by_id(self, item_id: int):
        start_time = time.time()
        try:
            query = """
            SELECT ads.id as item_id, ads.seller_id, users.is_verified_seller,
                   ads.title as name, ads.description, ads.category_id as category, ads.images_qty
            FROM ads
            JOIN users ON ads.seller_id = users.id
            WHERE ads.id = $1
            """
            row = await db.pool.fetchrow(query, item_id)
            return AdItem(**dict(row)) if row else None
        finally:
            duration = time.time() - start_time
            DB_QUERY_DURATION.labels(query_type="select").observe(duration)

    async def create_user(self, name: str, is_verified: bool):
        start_time = time.time()
        try:
            query = "INSERT INTO users (name, is_verified_seller) VALUES ($1, $2) RETURNING id"
            return await db.pool.fetchval(query, name, is_verified)
        finally:
            duration = time.time() - start_time
            DB_QUERY_DURATION.labels(query_type="insert").observe(duration)

    async def create_ad(self, seller_id: int, title: str, description: str, category: int, img_qty: int):
        start_time = time.time()
        try:
            query = """
            INSERT INTO ads (seller_id, title, description, category_id, images_qty)
            VALUES ($1, $2, $3, $4, $5) RETURNING id
            """
            return await db.pool.fetchval(query, seller_id, title, description, category, img_qty)
        finally:
            duration = time.time() - start_time
            DB_QUERY_DURATION.labels(query_type="insert").observe(duration)

    async def create_moderation_task(self, item_id: int) -> int:
        start_time = time.time()
        try:
            query = """
            INSERT INTO moderation_results (item_id, status)
            VALUES ($1, 'pending') RETURNING id
            """
            return await db.pool.fetchval(query, item_id)
        finally:
            duration = time.time() - start_time
            DB_QUERY_DURATION.labels(query_type="insert").observe(duration)

    async def update_moderation_task(self, task_id: int, status: str, 
                                     is_violation: bool = None, 
                                     probability: float = None, 
                                     error_message: str = None):
        start_time = time.time()
        try:
            query = """
            UPDATE moderation_results 
            SET status = $2, is_violation = $3, probability = $4, 
                error_message = $5, processed_at = NOW()
            WHERE id = $1
            """
            await db.pool.execute(query, task_id, status, is_violation, probability, error_message)
        finally:
            duration = time.time() - start_time
            DB_QUERY_DURATION.labels(query_type="update").observe(duration)

    async def get_moderation_task(self, task_id: int):
        start_time = time.time()
        try:
            query = "SELECT * FROM moderation_results WHERE id = $1"
            row = await db.pool.fetchrow(query, task_id)
            return dict(row) if row else None
        finally:
            duration = time.time() - start_time
            DB_QUERY_DURATION.labels(query_type="select").observe(duration)

    async def delete_ad_full(self, item_id: int):
        start_time = time.time()
        try:
            async with db.pool.acquire() as conn:
                async with conn.transaction():
                    await conn.execute("DELETE FROM moderation_results WHERE item_id = $1", item_id)
                    await conn.execute("DELETE FROM ads WHERE id = $1", item_id)
        finally:
            duration = time.time() - start_time
            DB_QUERY_DURATION.labels(query_type="delete").observe(duration)

ad_repo = AdRepository()