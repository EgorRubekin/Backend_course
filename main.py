import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager

from db import db 
from services.prediction import prediction_service
from services.kafka_producer import kafka_producer
from services.cache import cache_storage  

from routers.prediction import router as prediction_router
from routers.simple_predict import router as simple_predict_router
from routers.async_predict import router as async_router
from routers.ads import router as ads_router  

try:
    from routers.users import router as user_router, root_router
except ImportError:
    user_router = None
    root_router = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.connect() 
    await kafka_producer.start()
    prediction_service.startup()
    
    yield
    
    await kafka_producer.stop()
    await db.disconnect()
    await cache_storage.client.close()

app = FastAPI(
    title="Avito Moderation Service",
    lifespan=lifespan
)

app.include_router(prediction_router, tags=["Synchronous Prediction"])
app.include_router(simple_predict_router, tags=["DB Prediction"])
app.include_router(async_router, tags=["Asynchronous Prediction"]) 
app.include_router(ads_router, tags=["Ads Management"]) 

if user_router:
    app.include_router(user_router, prefix='/users', tags=["Users"])
if root_router:
    app.include_router(root_router, tags=["Auth"])

@app.get("/", tags=["Health"])
async def root():
    return {
        "message": "Avito Backend Course API",
        "db_status": "connected" if db.pool else "disconnected",
        "kafka_status": "ready" if kafka_producer.producer else "not_initialized",
        "redis_status": "connected" 
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8003, reload=True)