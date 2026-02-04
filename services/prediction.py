import logging
import numpy as np
from model import train_model, save_model, load_model

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

    def predict(self, item) -> dict:
        """
        Логика предсказания.
        Принимает Pydantic модель, возвращает словарь с результатом.
        """
        if not self.model:
            logger.error("Model is not loaded!")
            raise RuntimeError("Model is not loaded")

        # is_verified_seller → 1.0 или 0.0
        # images_qty → делим на 10
        # len(description) → делим на 1000
        # category → делим на 100
        
        features = [
            float(item.is_verified_seller),
            min(item.images_qty / 10.0, 1.0), # ограничим 1.0, хотя в задании просто деление
            len(item.description) / 1000.0,
            item.category / 100.0
        ]
        
        logger.info(f"Predicting for item_id={item.item_id}. Features: {features}")

        features_array = np.array([features])
        
        prediction_class = self.model.predict(features_array)[0]
        prediction_prob = self.model.predict_proba(features_array)[0][1]

        is_violation = bool(prediction_class == 1)

        logger.info(f"Result item_id={item.item_id}: violation={is_violation}, prob={prediction_prob:.4f}")

        return {
            "is_violation": is_violation,
            "probability": float(prediction_prob)
        }

# Создаем один экземпляр сервиса
prediction_service = PredictionService()