import numpy as np
from pathlib import Path
from KidneyClassifier.config.configuration import ConfigurationManager
from KidneyClassifier.components.ModelTrainingCNN import ModelTrainer
from KidneyClassifier import logger

STAGE_NAME = "Model Training"

class ModelTrainingCNNPipeline:
    def __init__(self):
        self.config = ConfigurationManager().get_model_training_config()

    def main(self):
        try:
            # Load preprocessed data
            processed_data = np.load('artifacts/data_preprocessing/preprocessed_data.npz')
            X_train, X_val = processed_data['X_train'], processed_data['X_test']
            y_train, y_val = processed_data['y_train'], processed_data['y_test']

            # Initialize and run model training
            trainer = ModelTrainer(self.config)
            
            # Pass data as separate tuples
            result = trainer.train(
                train_data=(X_train, y_train),
                val_data=(X_val, y_val)
            )
            
            if isinstance(result, tuple):
                model, history = result
                logger.info("Training completed successfully!")
            else:
                model = result
                logger.info("Loaded existing model successfully!")

        except Exception as e:
            logger.error(f"Error in {STAGE_NAME}: {e}")
            raise

if __name__ == '__main__':
    try:
        logger.info(f">>>>>> {STAGE_NAME} started <<<<<<")
        pipeline = TrainingPipeline()
        pipeline.main()
        logger.info(f">>>>>> {STAGE_NAME} completed <<<<<<")
    except Exception as e:
        logger.exception(e)
        raise