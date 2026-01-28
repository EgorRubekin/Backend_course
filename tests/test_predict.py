from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_predict_positive_verified():
    """Проверка: Подтвержденный продавец (даже без картинок) -> True"""
    payload = {
        "seller_id": 1,
        "is_verified_seller": True,
        "item_id": 100,
        "name": "Test Item",
        "description": "Desc",
        "category": 1,
        "images_qty": 0 
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    assert response.json() is True

def test_predict_positive_unverified_with_images():
    """Проверка: Неподтвержденный продавец, но есть картинки -> True"""
    payload = {
        "seller_id": 2,
        "is_verified_seller": False,
        "item_id": 101,
        "name": "Test Item",
        "description": "Desc",
        "category": 1,
        "images_qty": 1
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    assert response.json() is True

def test_predict_negative():
    """Проверка: Неподтвержденный продавец без картинок -> False"""
    payload = {
        "seller_id": 3,
        "is_verified_seller": False,
        "item_id": 102,
        "name": "Test Item",
        "description": "Desc",
        "category": 1,
        "images_qty": 0
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    assert response.json() is False

def test_validation_error_missing_field():
    """Проверка валидации: пропущено обязательное поле seller_id"""
    payload = {
        # "seller_id": 1, <--- Пропущено
        "is_verified_seller": False,
        "item_id": 103,
        "name": "Error",
        "description": "Desc",
        "category": 1,
        "images_qty": 1
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 422 # Ошибка валидации

def test_validation_error_wrong_type():
    """Проверка валидации: images_qty передан как строка, которую нельзя перевести в int"""
    payload = {
        "seller_id": 4,
        "is_verified_seller": False,
        "item_id": 104,
        "name": "Error",
        "description": "Desc",
        "category": 1,
        "images_qty": "two" # Ошибка типа
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 422

def test_validation_negative_images():
    """Проверка валидации: количество картинок меньше 0"""
    payload = {
        "seller_id": 5,
        "is_verified_seller": False,
        "item_id": 105,
        "name": "Error",
        "description": "Desc",
        "category": 1,
        "images_qty": -1
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 422