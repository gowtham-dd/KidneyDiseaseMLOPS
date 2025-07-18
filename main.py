from src.KidneyClassifier import logger
from src.KidneyClassifier.pipeline.Data_Ingestion_pipeline import DataIngestionTrainingPipeline
# from src.KidneyClassifier.pipeline.Data_Validation_pipeline import DataValidationTrainingPipeline
# from src.KidneyClassifier.pipeline.Data_Transformation_pipeline import DataTransformationTrainingPipeline
# from src.KidneyClassifier.pipeline.Model_Training_Pipeline import ModelTrainerPipeline
# from src.KidneyClassifier.pipeline.Model_Evaluation_pipeline import ModelEvaluationPipeline
# import dagshub
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