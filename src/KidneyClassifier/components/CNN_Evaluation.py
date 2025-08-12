import numpy as np
import tensorflow as tf
import mlflow
from KidneyClassifier.utils.common import save_json
from KidneyClassifier import logger

class ModelEvaluation:
    def __init__(self, config):
        self.config = config

    def _load_model(self):
        # Load Keras saved model, not generic TF SavedModel
        model = tf.keras.models.load_model(str(self.config.model_path))
        return model

    def evaluate_model(self):
        # Load test data
        test_data = np.load(self.config.test_data_path)
        X_test, y_test = test_data['X_test'], test_data['y_test']

        # Convert to float32 if needed
        if X_test.dtype == np.float64:
            X_test = X_test.astype(np.float32)

        # Load Keras model
        model = self._load_model()

        # Predict using Keras model
        y_pred_probs = model.predict(X_test, batch_size=self.config.batch_size)
        y_pred = np.argmax(y_pred_probs, axis=1)

        # Calculate metrics
        accuracy = np.mean(y_test == y_pred)
        precision = tf.keras.metrics.Precision()(y_test, y_pred).numpy()
        recall = tf.keras.metrics.Recall()(y_test, y_pred).numpy()
        f1 = 2 * (precision * recall) / (precision + recall + 1e-7)  # small epsilon to avoid div by zero

        metrics = {
            "accuracy": float(accuracy),
            "precision": float(precision),
            "recall": float(recall),
            "f1_score": float(f1)
        }

        save_json(path=self.config.metric_file_name, data=metrics)
        logger.info(f"Evaluation metrics: {metrics}")
        return metrics
    
    def log_into_mlflow(self):
        mlflow.set_tracking_uri(self.config.mlflow_uri)

        try:
            with mlflow.start_run():
            # ✅ Log all parameters
                mlflow.log_params(self.config.all_params)

            # Evaluate and log metrics
                metrics = self.evaluate_model()
                mlflow.log_metrics(metrics)

            # Log model
                mlflow.tensorflow.log_model(
                model=tf.keras.models.load_model(self.config.model_path),
                artifact_path="kidney_model",
                registered_model_name="Kidney_SavedModel"
            )

                logger.info("MLflow logging completed successfully")

        except Exception as e:
            logger.error(f"MLflow logging failed: {e}")
            if mlflow.active_run():
                mlflow.end_run(status="FAILED")
            raise
