from db import db

class UserRepository:
    async def get_user_by_id(self, user_id: int):
        async with db.pool.acquire() as conn:
            return await conn.fetchrow("SELECT * FROM users WHERE id = $1", user_id)

    async def create_user(self, name: str, password_hash: str):
        async with db.pool.acquire() as conn:
            return await conn.fetchval(
                "INSERT INTO users (name, password_hash) VALUES ($1, $2) RETURNING id",
                name, password_hash
            )

    async def delete_user(self, user_id: int):
        async with db.pool.acquire() as conn:
            await conn.execute("DELETE FROM users WHERE id = $1", user_id)

user_repo = UserRepository()