from src.ChestDiseaseRadio import logger
from src.ChestDiseaseRadio.pipeline.Data_Ingestion_pipeline import DataIngestionTrainingPipeline
from src.ChestDiseaseRadio.pipeline.Prepare_Base_Model_pipeline import PrepareBaseModelPipeline
from src.ChestDiseaseRadio.pipeline.Model_Training_Pipeline import ModelTrainingPipeline

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



STAGE_NAME="Preparing Base Model stage"


try:
    logger.info(f">>>> Stage {STAGE_NAME} started")
    obj=PrepareBaseModelPipeline()
    obj.main()
    logger.info(f">>>>> Stage {STAGE_NAME} completed")

except Exception as e:
    logger.exception(e)
    raise e




STAGE_NAME="Model Training stage"


try:
    logger.info(f">>>> Stage {STAGE_NAME} started")
    obj=ModelTrainingPipeline()
    obj.main()
    logger.info(f">>>>> Stage {STAGE_NAME} completed")

except Exception as e:
    logger.exception(e)
    raise e