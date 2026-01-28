from fastapi import FastAPI
from pydantic import BaseModel, Field
import uvicorn

from routers.users import router as user_router, root_router

app = FastAPI()


class AdItem(BaseModel):
    seller_id: int
    is_verified_seller: bool
    item_id: int
    name: str
    description: str
    category: int
    images_qty: int = Field(..., ge=0, description="Количество изображений")


@app.post("/predict")
async def predict(item: AdItem) -> bool:
    """
    Эндпоинт для модерации.
    Возвращает True (одобрено) или False (отклонено).

    Логика: если пользователь подтвержденный - то он всегда проходит проверку
    Неподтвержденные пользователи проходят только при наличии изображений
    Иначе отказ
    """

    if item.is_verified_seller:
        return True

    if item.images_qty > 0:
        return True

    return False


app.include_router(user_router, prefix='/users')
app.include_router(root_router)


@app.get("/")
async def root():
    return {'message': 'Hello World'}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)