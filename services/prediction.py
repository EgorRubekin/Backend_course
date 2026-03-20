import logging
import numpy as np
import pickle
import time
import os
import mlflow
import mlflow.sklearn
from models.prediction import PredictionRequest
from app.metrics import (
    PREDICTIONS_TOTAL, 
    PREDICTION_DURATION, 
    PREDICTION_ERRORS, 
    MODEL_PROBABILITY
)

logger = logging.getLogger(__name__)

class PredictionService:
    def __init__(self, model_path: str = "model.pkl"):
        self.model_path = model_path
        self.model = None

    def startup(self):
        use_mlflow = os.getenv("USE_MLFLOW", "false").lower() == "true"
        
        if use_mlflow:
            try:
                mlflow.set_tracking_uri("sqlite:///mlflow.db")
                model_name = "moderation-model"
                stage = "Production"
                model_uri = f"models:/{model_name}/{stage}"
                
                self.model = mlflow.sklearn.load_model(model_uri)
                logger.info(f"Модель успешно загружена из MLflow Registry: {model_uri}")
            except Exception as e:
                logger.error(f"Не удалось загрузить модель из MLflow: {e}. Откат к локальному файлу.")
                self._load_local_model()
        else:
            self._load_local_model()

    def _load_local_model(self):
        try:
            if os.path.exists(self.model_path):
                with open(self.model_path, "rb") as f:
                    self.model = pickle.load(f)
                logger.info(f"Модель загружена локально из {self.model_path}")
            else:
                logger.error(f"Файл {self.model_path} не найден!")
        except Exception as e:
            logger.error(f"Ошибка при загрузке локальной модели: {e}")

    def predict(self, item) -> dict:

        if not self.model:
            PREDICTION_ERRORS.labels(error_type="model_not_loaded").inc()
            logger.error("Попытка предсказания без загруженной модели")
            raise RuntimeError("ML модель не загружена. Проверьте логи старта.")

        try:

            features = [
                float(getattr(item, 'is_verified_seller', 0)),
                float(min(getattr(item, 'images_qty', 0) / 10.0, 1.0)),
                float(len(getattr(item, 'description', "")) / 1000.0),
                float(getattr(item, 'category', 0) / 100.0)
            ]
            
            features_array = np.array([features])
            
            start_time = time.time()
            
            prediction_class = self.model.predict(features_array)[0]
            prediction_prob = self.model.predict_proba(features_array)[0][1]
            
            duration = time.time() - start_time

            is_violation = bool(prediction_class == 1)
            res_label = "violation" if is_violation else "no_violation"

            PREDICTIONS_TOTAL.labels(result=res_label).inc()
            PREDICTION_DURATION.observe(duration)
            MODEL_PROBABILITY.observe(float(prediction_prob))

            logger.info(f"Предсказание выполнено: violation={is_violation}, prob={prediction_prob:.4f}")

            return {
                "is_violation": is_violation,
                "probability": float(prediction_prob)
            }

        except Exception as e:
            PREDICTION_ERRORS.labels(error_type="prediction_runtime_error").inc()
            logger.error(f"Ошибка во время инференса модели: {e}")
            raise e

# Создаем синглтон сервиса
prediction_service = PredictionService()