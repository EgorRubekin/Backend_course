from pydantic import BaseModel, Field

class AdItem(BaseModel):
    seller_id: int
    is_verified_seller: bool
    item_id: int
    name: str
    description: str
    category: int
    images_qty: int = Field(..., ge=0, description="Количество изображений")

class PredictionResponse(BaseModel):
    is_violation: bool
    probability: float