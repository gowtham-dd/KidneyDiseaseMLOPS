import os
import tensorflow as tf
from pathlib import Path
import joblib   # ✅ REQUIRED for XGB

class ModelTrainer:
    def __init__(self, config):
        self.config = config
        self.xgb_path = Path("artifacts/model_training/pnemonia/xgb_model.pkl")

    # ✅ Check if XGB exists
    def _model_exists(self):
        return self.xgb_path.exists()

    # ✅ Load XGB
    def load_xgb_model(self):
        print(f"Loading XGBoost model from {self.xgb_path}")
        return joblib.load(self.xgb_path)

    def build_model(self):
        model = tf.keras.Sequential([
            # Your CNN layers
        ])
        model.compile(
            optimizer='adam',
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        return model

    def train(self, train_data, val_data):

        # ✅ PRIORITY: XGB
        if self._model_exists():
            print("XGBoost model found. Skipping CNN training...")
            return {
                "type": "xgb",
                "model": self.load_xgb_model()
            }

        # ❌ No XGB → Train CNN
        print("No XGBoost model found. Training CNN model...")

        model = self.build_model()

        history = model.fit(
            train_data[0], train_data[1],
            validation_data=val_data,
            epochs=self.config.epochs,
            batch_size=self.config.batch_size
        )

        # ✅ Save CNN properly
        model.save(self.config.trained_model_path)

        print(f"CNN model saved to {self.config.trained_model_path}")

        return {
            "type": "cnn",
            "model": model,
            "history": history
        }