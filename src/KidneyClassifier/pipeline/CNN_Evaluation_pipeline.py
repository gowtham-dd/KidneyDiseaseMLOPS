from KidneyClassifier.config.configuration import ConfigurationManager
from KidneyClassifier.components.CNN_Evaluation import ModelEvaluation
from KidneyClassifier import logger

STAGE_NAME = "Evaluation stage"


class CNNEvaluationPipeline:
    def __init__(self):
        pass

    def main(self):
        config = ConfigurationManager()
        eval_config = config.get_model_evaluation_config()
        model_evaluator = ModelEvaluation(config=eval_config)  # Now works correctly
        model_evaluator.log_into_mlflow()



if __name__ == '__main__':
    try:
        logger.info(f">>>>>> stage {STAGE_NAME} started <<<<<<")
        obj = CNNEvaluationPipeline()
        obj.main()
        logger.info(f">>>>>> stage {STAGE_NAME} completed <<<<<<\n\nx==========x")
    except Exception as e:
        logger.exception(e)
        raise e