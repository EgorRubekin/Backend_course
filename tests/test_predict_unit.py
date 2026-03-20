import pytest
from unittest.mock import MagicMock
from services.prediction import PredictionService

@pytest.mark.parametrize("img_qty, expected_violation", [
    (0, True),   
    (100, False), 
])
def test_prediction_logic_mock(img_qty, expected_violation):
    service = PredictionService()
    service.model = MagicMock()
    
    service.model.predict.return_value = [expected_violation]
    service.model.predict_proba.return_value = [[0.2, 0.8]]
    
    from models.prediction import PredictionRequest
    mock_data = PredictionRequest(
        seller_id=1, is_verified_seller=True, item_id=10,
        name="Test", description="Desc", category=1, images_qty=img_qty
    )
    
    result = service.predict(mock_data)
    assert result["is_violation"] == expected_violation