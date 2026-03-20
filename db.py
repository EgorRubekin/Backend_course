import os
import asyncpg

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5435/hw")

class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        # Добавим проверку, чтобы не переподключаться лишний раз
        if self.pool is None or self.pool._closed:
            self.pool = await asyncpg.create_pool(DATABASE_URL)

    async def disconnect(self):
        if self.pool:
            await self.pool.close()
            self.pool = None

db = Database()