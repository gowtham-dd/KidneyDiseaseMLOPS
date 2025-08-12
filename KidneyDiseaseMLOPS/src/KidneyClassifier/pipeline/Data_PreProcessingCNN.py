from KidneyClassifier.config.configuration import ConfigurationManager
from pathlib import Path
from KidneyClassifier.components.Data_PreProcessingCNN import DataPreprocessing
from KidneyClassifier import logger

STAGE_NAME = "Data Preprocessing"

class DataPreprocessingTrainingPipeline:
    def __init__(self):
        pass

    def main(self):
        try:
            config = ConfigurationManager()
            preprocessing_config = config.get_data_preprocessing_config()

            raw_data_path = Path(config.get_data_ingestion_config().unzip_dir) / "CT-KIDNEY-DATASET"

            data_preprocessor = DataPreprocessing(preprocessing_config, data_dir=str(raw_data_path))
            
            # This will automatically check for existing processed data
            X_train, X_test, y_train, y_test = data_preprocessor.load_and_preprocess_images()
            
            logger.info(f"Preprocessing complete. Train shape: {X_train.shape}, Test shape: {X_test.shape}")
            
        except Exception as e:
            logger.error(f"Error in {STAGE_NAME}: {e}")
            raise

if __name__ == '__main__':
    try:
        logger.info(f">>>>>> {STAGE_NAME} started <<<<<<")
        obj = DataPreprocessingTrainingPipeline()
        obj.main()
        logger.info(f">>>>>> {STAGE_NAME} completed <<<<<<\n\nx==========x")
    except Exception as e:
        logger.exception(e)
        raise e