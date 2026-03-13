from fastapi import APIRouter, Response, Cookie, Depends, HTTPException, status
from pydantic import BaseModel
from services.auth import auth_service
from repositories.account import account_repo
from models.account import AccountModel

router = APIRouter()

class LoginSchema(BaseModel):
    login: str
    password: str

async def get_current_account(access_token: str = Cookie(None)) -> AccountModel:
    if not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    account_id = auth_service.decode_token(access_token)
    if not account_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    account = await account_repo.get_by_id(account_id)
    if not account or account.is_blocked:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account blocked or not found")

    return account

@router.post("/login", tags=["Auth"])
async def login(data: LoginSchema, response: Response):
    account = await account_repo.get_by_login_and_password(data.login, data.password)
    if not account:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong login or password")

    token = auth_service.create_token(account.id)
    response.set_cookie(key="access_token", value=token, httponly=True)
    return {"message": "Logged in", "account_id": account.id}