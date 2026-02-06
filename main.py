from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn

from db import db 
from services.prediction import prediction_service
from routers.prediction import router as prediction_router
from routers.simple_predict import router as simple_predict_router

try:
    from routers.users import router as user_router, root_router
except ImportError:
    user_router = None
    root_router = None

@asynccontextmanager
async def lifespan(app: FastAPI):

    await db.connect() 
    prediction_service.startup()
    yield
    await db.disconnect()

app = FastAPI(lifespan=lifespan)

app.include_router(prediction_router)
app.include_router(simple_predict_router) # Наш новый роутер для БД

if user_router:
    app.include_router(user_router, prefix='/users')
if root_router:
    app.include_router(root_router)

@app.get("/")
async def root():
    return {"message": "Hello World", "db_status": "connected"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)