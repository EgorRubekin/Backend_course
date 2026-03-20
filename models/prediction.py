from pydantic import BaseModel, Field

class PredictionRequest(BaseModel):
    seller_id: int = Field(..., gt=0, description="ID продавца")
    is_verified_seller: bool
    item_id: int = Field(..., gt=0, description="ID объявления")
    name: str = Field(..., min_length=2, max_length=200)
    description: str
    category: int = Field(..., ge=0)
    images_qty: int = Field(..., ge=0, description="Количество изображений не может быть отрицательным")

class PredictionResponse(BaseModel):
    is_violation: bool
    probability: float