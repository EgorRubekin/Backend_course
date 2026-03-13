import pytest
from pytest_asyncio import fixture as async_fixture
from fastapi import HTTPException

from db import db
from repositories.account import account_repo
from services.auth import auth_service
from routers.auth import get_current_account

@async_fixture(autouse=True, scope="function")
async def setup_db():
    await db.connect()
    yield
    await db.disconnect()


def test_auth_service_token_cycle():
    account_id = 123
    token = auth_service.create_token(account_id)
    assert isinstance(token, str)
    
    decoded_id = auth_service.decode_token(token)
    assert decoded_id == account_id

def test_auth_service_invalid_token():
    assert auth_service.decode_token("not-a-token") is None

@pytest.mark.asyncio
async def test_get_current_account_no_token():
    with pytest.raises(HTTPException) as exc:
        await get_current_account(access_token=None)
    assert exc.value.status_code == 401


@pytest.mark.integration
@pytest.mark.asyncio
async def test_account_repo_workflow():
    login = "test_user_unique" 
    password = "secret_password"
    
    acc_id = await account_repo.create(login, password)
    assert acc_id is not None
    
    account = await account_repo.get_by_login_and_password(login, password)
    assert account is not None
    assert account.login == login
    
    await account_repo.block(acc_id)
    updated_acc = await account_repo.get_by_id(acc_id)
    assert updated_acc.is_blocked is True
    
    await account_repo.delete(acc_id)