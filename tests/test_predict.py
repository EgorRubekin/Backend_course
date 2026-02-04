import pytest
from fastapi.testclient import TestClient
from main import app
from services.prediction import prediction_service


@pytest.fixture
def client():

    with TestClient(app) as c:
        yield c


test_cases = [
    ("Verified User", True, 5, 200),
    ("Unverified User", False, 0, 200),
    ("Many Images", False, 10, 200),
]

@pytest.mark.parametrize("name, is_verified, img_qty, expected_status", test_cases)
def test_predict_success_scenarios(client, name, is_verified, img_qty, expected_status):
    """Проверяет успешные сценарии предсказания"""
    payload = {
        "seller_id": 1,
        "is_verified_seller": is_verified,
        "item_id": 100,
        "name": name,
        "description": "Test description",
        "category": 1,
        "images_qty": img_qty
    }
    response = client.post("/predict", json=payload)
    
    assert response.status_code == expected_status
    data = response.json()
    assert "is_violation" in data
    assert "probability" in data
    assert isinstance(data["is_violation"], bool)
    assert isinstance(data["probability"], float)

def test_validation_error(client):
    """Проверка ошибки 422 при неверных типах данных"""
    payload = {
        "seller_id": "STING_INSTEAD_OF_INT",
        "is_verified_seller": False,
        "item_id": 100,
        "name": "Test",
        "description": "Desc",
        "category": 1,
        "images_qty": 5
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 422

def test_model_unavailable_error(client):
    """Проверка ошибки 503, если модель принудительно удалена"""
    # Сохраняем реальную модель
    original_model = prediction_service.model
    # Имитируем отсутствие модели
    prediction_service.model = None
    
    payload = {
        "seller_id": 1,
        "is_verified_seller": False,
        "item_id": 100,
        "name": "Test",
        "description": "Desc",
        "category": 1,
        "images_qty": 5
    }
    
    response = client.post("/predict", json=payload)
    assert response.status_code == 503
    
    # Возвращаем модель на место
    prediction_service.model = original_model