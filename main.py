from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn

from routers.prediction import router as prediction_router
from services.prediction import prediction_service

try:
    from routers.users import router as user_router, root_router
except ImportError:
    user_router = None
    root_router = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    prediction_service.startup()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(prediction_router)

if user_router:
    app.include_router(user_router, prefix='/users')
if root_router:
    app.include_router(root_router)

@app.get("/")
async def root():
    return {'message': 'Hello World'}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)