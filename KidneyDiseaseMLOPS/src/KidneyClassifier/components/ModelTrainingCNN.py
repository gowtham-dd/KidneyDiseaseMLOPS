import os
import tensorflow as tf
from pathlib import Path

class ModelTrainer:
    def __init__(self, config):
        self.config = config

    def _model_exists(self):
        """Check if model exists with all required SavedModel files"""
        model_dir = Path(self.config.trained_model_path)
        required_files = {
            'saved_model.pb',
            'variables/variables.index',
            'variables/variables.data-00000-of-00001'
        }
        return all((model_dir / file).exists() for file in required_files)

    def build_model(self):
        """Your existing model building code"""
        model = tf.keras.Sequential([
            # Your model layers here
            # ...
        ])
        model.compile(
            optimizer='adam',
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        return model

    def train(self, train_data, val_data):
        """Train or load existing model with proper SavedModel handling"""
        # Check if valid model exists
        if self._model_exists():
            print(f"Loading existing SavedModel from {self.config.trained_model_path}")
            try:
                # First try loading as Keras model
                return tf.keras.models.load_model(self.config.trained_model_path)
            except Exception as e:
                print(f"Keras loading failed: {e}\nLoading as generic SavedModel...")
                return tf.saved_model.load(self.config.trained_model_path)

        print("No valid model found. Training new model...")
        model = self.build_model()
        
        # Your training code
        history = model.fit(
            train_data[0], train_data[1],
            validation_data=val_data,
            epochs=self.config.epochs,
            batch_size=self.config.batch_size
        )

        # Save in proper Keras-compatible SavedModel format
        tf.keras.models.save_model(
            model,
            self.config.trained_model_path,
            save_format='tf'  # Creates proper SavedModel with Keras metadata
        )
        print(f"Model saved to {self.config.trained_model_path}")
        
        return model, history