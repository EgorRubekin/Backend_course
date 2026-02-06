import asyncpg
from contextlib import asynccontextmanager

DATABASE_URL = "postgresql://postgres:1234@localhost:5432/avito_shop"

class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        if self.pool and self.pool._closed:
            self.pool = None
            
        if self.pool is None:
            self.pool = await asyncpg.create_pool(DATABASE_URL)

    async def disconnect(self):
        if self.pool:
            try:
                await self.pool.close()
            except (RuntimeError, AttributeError):
                pass
            finally:
                self.pool = None

db = Database()