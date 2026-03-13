import hashlib
from typing import Optional
from db import db
from models.account import AccountModel

def hash_password(password: str) -> str:
    return hashlib.md5(password.encode()).hexdigest()

class AccountRepository:
    async def create(self, login: str, password: str) -> int:
        query = "INSERT INTO account (login, password) VALUES ($1, $2) RETURNING id"
        return await db.pool.fetchval(query, login, hash_password(password))

    async def get_by_id(self, account_id: int) -> Optional[AccountModel]:
        query = "SELECT * FROM account WHERE id = $1"
        row = await db.pool.fetchrow(query, account_id)
        return AccountModel(**dict(row)) if row else None

    async def get_by_login_and_password(self, login: str, password: str) -> Optional[AccountModel]:
        query = "SELECT * FROM account WHERE login = $1 AND password = $2"
        row = await db.pool.fetchrow(query, login, hash_password(password))
        return AccountModel(**dict(row)) if row else None

    async def block(self, account_id: int):
        query = "UPDATE account SET is_blocked = TRUE WHERE id = $1"
        await db.pool.execute(query, account_id)

    async def delete(self, account_id: int):
        query = "DELETE FROM account WHERE id = $1"
        await db.pool.execute(query, account_id)

account_repo = AccountRepository()