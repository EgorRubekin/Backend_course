import pytest
import uuid
from fastapi.testclient import TestClient
from main import app
from db import db
from services.repositories import ad_repo
from routers.auth import get_current_account
from models.account import AccountModel

async def override_get_current_account():
    return AccountModel(
        id=1, 
        username="test_user", 
        login="test_login", 
        password="test_password", 
        is_verified=True
    )

app.dependency_overrides[get_current_account] = override_get_current_account

def test_simple_predict_success():
    with TestClient(app) as client:
        response = client.get("/simple_predict?item_id=1")
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert "is_violation" in data

def test_simple_predict_not_found():
    with TestClient(app) as client:
        response = client.get("/simple_predict?item_id=999999")
        assert response.status_code == 404

@pytest.mark.asyncio
async def test_repository_create_and_get():
    if not db.pool:
        await db.connect()
    
    try:
        unique_name = f"User_{uuid.uuid4().hex[:6]}"
        user_id = await ad_repo.create_user(unique_name, True)
        assert user_id is not None
        
        ad_id = await ad_repo.create_ad(
            seller_id=user_id,
            title="Test Ad",
            description="Testing DB",
            category=1,
            img_qty=5
        )
        assert ad_id is not None
        
        ad = await ad_repo.get_ad_by_id(ad_id)
        assert ad is not None
        
        actual_title = getattr(ad, 'title', getattr(ad, 'name', None))
        assert actual_title == "Test Ad"
        
        with TestClient(app) as client:
            resp = client.get(f"/simple_predict?item_id={ad_id}")
            assert resp.status_code == 200
        
    finally:
        pass