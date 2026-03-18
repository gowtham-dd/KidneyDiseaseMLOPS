from src.ChestDiseaseRadio import logger
from src.ChestDiseaseRadio.pipeline.Data_Ingestion_pipeline import DataIngestionTrainingPipeline
from src.ChestDiseaseRadio.pipeline.Data_PreProcessingCNN import DataPreprocessingTrainingPipeline
from src.ChestDiseaseRadio.pipeline.Model_Training_CNN_pipeline import ModelTrainingCNNPipeline
from src.ChestDiseaseRadio.pipeline.CNN_Evaluation_pipeline import CNNEvaluationPipeline

# dagshub.init(repo_owner='gowtham-dd', repo_name='Introvert-Vs-Extrovert', mlflow=True)


STAGE_NAME="Data Ingestion stage"


try:
    logger.info(f">>>> Stage {STAGE_NAME} started")
    obj=DataIngestionTrainingPipeline()
    obj.main()
    logger.info(f">>>>> Stage {STAGE_NAME} completed")

except Exception as e:
    logger.exception(e)
    raise e





STAGE_NAME="Data PreProcessing CNN stage"


try:
    logger.info(f">>>> Stage {STAGE_NAME} started")
    obj=DataPreprocessingTrainingPipeline()
    obj.main()
    logger.info(f">>>>> Stage {STAGE_NAME} completed")

except Exception as e:
    logger.exception(e)
    raise e




STAGE_NAME="Model Training CNN stage"


try:
    logger.info(f">>>> Stage {STAGE_NAME} started")
    obj=ModelTrainingCNNPipeline()
    obj.main()
    logger.info(f">>>>> Stage {STAGE_NAME} completed")

except Exception as e:
    logger.exception(e)
    raise e



STAGE_NAME="Model Evaluation CNN stage"


try:
    logger.info(f">>>> Stage {STAGE_NAME} started")
    obj=CNNEvaluationPipeline()
    obj.main()
    logger.info(f">>>>> Stage {STAGE_NAME} completed")

except Exception as e:
    logger.exception(e)
    raise e

