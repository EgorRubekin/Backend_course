import mlflow
import mlflow.sklearn
import pickle
import os
from sklearn.linear_model import LogisticRegression
import numpy as np

def register():
    mlflow.set_tracking_uri("sqlite:///mlflow.db")
    mlflow.set_experiment("moderation-model")

    model_name = "moderation-model"
    model_path = "model.pkl"

    if not os.path.exists(model_path):
        print(f"Файл {model_path} не найден. Создаю временную модель...")
        model = LogisticRegression()
        X = np.array([[0, 0, 0, 0], [1, 1, 1, 1]])
        y = np.array([0, 1])
        model.fit(X, y)
        with open(model_path, "wb") as f:
            pickle.dump(model, f)
    else:
        with open(model_path, "rb") as f:
            model = pickle.load(f)

    print("Регистрируем модель в MLflow...")
    with mlflow.start_run():
        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="model",
            registered_model_name=model_name
        )
    
    client = mlflow.tracking.MlflowClient()
    latest_version = client.get_latest_versions(model_name, stages=["None"])[0].version
    client.transition_model_version_stage(
        name=model_name,
        version=latest_version,
        stage="Production"
    )
    
    print(f"Успех! Модель '{model_name}' версия {latest_version} теперь в статусе Production.")

if __name__ == "__main__":
    register()