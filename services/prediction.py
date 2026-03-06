import logging
import numpy as np
from model import train_model, save_model, load_model
from services.repositories import ad_repo
import time
import logging
from app.metrics import (
    PREDICTIONS_TOTAL, 
    PREDICTION_DURATION, 
    PREDICTION_ERRORS, 
    MODEL_PROBABILITY
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class PredictionService:
    def __init__(self):
        self.model = None

    def startup(self):
        """Загрузка или обучение модели при старте"""
        logger.info("Service starting...")
        self.model = load_model()
        
        if self.model is None:
            logger.info("Model not found. Training new model...")
            self.model = train_model()
            save_model(self.model)
            logger.info("Model trained and saved.")
        else:
            logger.info("Model loaded from disk.")

    async def predict_by_id(self, item_id: int):
        """Получает данные из БД по ID и делает предсказание"""

        item = await ad_repo.get_ad_by_id(item_id)
        
        if not item:
            return None
            
        return self.predict(item)	 

    def predict(self, item) -> dict:
        start_time = time.time()
        
        if not self.model:
            PREDICTION_ERRORS.labels(error_type="model_unavailable").inc()
            logger.error("Model is not loaded!")
            raise RuntimeError("Model is not loaded")

        try:
            features = [
                float(item.is_verified_seller),
                min(item.images_qty / 10.0, 1.0),
                len(item.description) / 1000.0,
                item.category / 100.0
            ]
            features_array = np.array([features])
            
            inference_start = time.time()
            prediction_class = self.model.predict(features_array)[0]
            prediction_prob = self.model.predict_proba(features_array)[0][1]
            PREDICTION_DURATION.observe(time.time() - inference_start)

            is_violation = bool(prediction_class == 1)

            res_label = "violation" if is_violation else "no_violation"

            

            PREDICTIONS_TOTAL.labels(result=res_label).inc()
            MODEL_PROBABILITY.observe(float(prediction_prob))

            return {
                "is_violation": is_violation,
                "probability": float(prediction_prob)
            }

        except Exception as e:
            PREDICTION_ERRORS.labels(error_type="prediction_error").inc()
            logger.error(f"Prediction error: {e}")
            raise e

prediction_service = PredictionService()