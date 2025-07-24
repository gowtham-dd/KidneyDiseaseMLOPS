from src.KidneyClassifier.constant import *
from src.KidneyClassifier.utils.common import read_yaml,create_directories 
from src.KidneyClassifier.entity.config_entitiy import DataIngestionConfig,PrepareBaseModelConfig,TrainingConfig,DataPreprocessingConfig,ModelTrainingConfig,ModelEvaluationConfig
import os
class ConfigurationManager:
    def __init__(
        self,
        config_filepath = CONFIG_FILE_PATH,
        params_filepath = PARAMS_FILE_PATH,
):

        self.config = read_yaml(config_filepath)
        self.params = read_yaml(params_filepath)

        create_directories([self.config.artifacts_root])


    
    def get_data_ingestion_config(self) -> DataIngestionConfig:
        config = self.config.data_ingestion

        create_directories([config.root_dir])

        data_ingestion_config = DataIngestionConfig(
            root_dir=config.root_dir,
            source_URL=config.source_URL,
            local_data_file=config.local_data_file,
            unzip_dir=config.unzip_dir ,
            unzipped_data_dir=config.unzipped_data_dir
        )

        return data_ingestion_config
    


    def get_prepare_base_model_config(self) -> PrepareBaseModelConfig:
        config = self.config.prepare_base_model
        
        create_directories([config.root_dir])

        prepare_base_model_config = PrepareBaseModelConfig(
            root_dir=Path(config.root_dir),
            base_model_path=Path(config.base_model_path),
            updated_base_model_path=Path(config.updated_base_model_path),
            params_image_size=self.params.IMAGE_SIZE,
            params_learning_rate=self.params.LEARNING_RATE,
            params_include_top=self.params.INCLUDE_TOP,
            params_weights=self.params.WEIGHTS,
            params_classes=self.params.CLASSES
        )

        return prepare_base_model_config






    
    def get_training_config(self) -> TrainingConfig:
        training = self.config.training
        prepare_base_model = self.config.prepare_base_model
        params = self.params
        training_data = os.path.join(self.config.data_ingestion.unzip_dir, "CT-KIDNEY-DATASET")
        create_directories([
            Path(training.root_dir)
        ])

        training_config = TrainingConfig(
            root_dir=Path(training.root_dir),
            trained_model_path=Path(training.trained_model_path),
            updated_base_model_path=Path(prepare_base_model.updated_base_model_path),
            training_data=Path(training_data),
            params_epochs=params.EPOCHS,
            params_batch_size=params.BATCH_SIZE,
            params_is_augmentation=params.AUGMENTATION,
            params_image_size=params.IMAGE_SIZE
        )

        return training_config
    
    def get_data_preprocessing_config(self) -> DataPreprocessingConfig:
        config = self.config.data_preprocessing
        create_directories([config.root_dir])

        return DataPreprocessingConfig(
            root_dir=Path(config.root_dir),
            processed_data_file=Path(config.processed_data_file),
            image_size=config.image_size
        )



    def get_model_training_config(self) -> ModelTrainingConfig:
        config = self.config.model_training
        params = self.params.model_training
        
        create_directories([config.model_dir])

        return ModelTrainingConfig(
            root_dir=Path(config.model_dir),
            trained_model_path=Path(config.trained_model_path),
            input_shape=tuple(params.input_shape),
            epochs=params.epochs,
            batch_size=params.batch_size,
            validation_split=params.validation_split,
            learning_rate=params.learning_rate
        )



    
    def get_model_evaluation_config(self) -> ModelEvaluationConfig:
        config = self.config.model_evaluation
        params = self.params.model_evaluation  # or whatever group you use

        create_directories([config.root_dir])

        return ModelEvaluationConfig(
        root_dir=Path(config.root_dir),
        test_data_path=Path(config.test_data_path),
        model_path=Path(config.model_path),
        metric_file_name=Path(config.metric_file_name),
        mlflow_uri=config.mlflow_uri,
        batch_size=params.batch_size,
        target_metric=params.target_metric,
        all_params=params  
        )

