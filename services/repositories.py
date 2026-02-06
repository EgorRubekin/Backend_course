from db import db
from models.prediction import AdItem

class AdRepository:

    async def get_ad_by_id(self, item_id: int):
        query = """
        SELECT ads.id as item_id, ads.seller_id, users.is_verified_seller,
               ads.title as name, ads.description, ads.category_id as category, ads.images_qty
        FROM ads
        JOIN users ON ads.seller_id = users.id
        WHERE ads.id = $1
        """
        row = await db.pool.fetchrow(query, item_id)
        return AdItem(**dict(row)) if row else None

    async def create_user(self, name: str, is_verified: bool):
        query = "INSERT INTO users (name, is_verified_seller) VALUES ($1, $2) RETURNING id"
        return await db.pool.fetchval(query, name, is_verified)

    async def create_ad(self, seller_id: int, title: str, description: str, category: int, img_qty: int):
        query = """
        INSERT INTO ads (seller_id, title, description, category_id, images_qty)
        VALUES ($1, $2, $3, $4, $5) RETURNING id
        """
        return await db.pool.fetchval(query, seller_id, title, description, category, img_qty)

ad_repo = AdRepository()