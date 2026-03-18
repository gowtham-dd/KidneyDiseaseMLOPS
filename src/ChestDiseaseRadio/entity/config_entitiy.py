## ENTITY
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class DataIngestionConfig:
    root_dir:Path
    source_URL:str
    local_data_file:Path
    unzip_dir:Path
    unzipped_data_dir:Path
    


@dataclass(frozen=True)
class PrepareBaseModelConfig:
    root_dir: Path
    base_model_path: Path
    updated_base_model_path: Path
    params_image_size: list
    params_learning_rate: float
    params_include_top: bool
    params_weights: str
    params_classes: int



@dataclass(frozen=True)
class TrainingConfig:
    root_dir: Path
    trained_model_path: Path
    updated_base_model_path: Path
    training_data: Path
    params_epochs: int
    params_batch_size: int
    params_is_augmentation: bool
    params_image_size: list



@dataclass(frozen=True)
class DataPreprocessingConfig:
    root_dir: Path
    processed_data_file: Path
    image_size: int


@dataclass(frozen=True)
class ModelTrainingConfig:
    root_dir: Path
    trained_model_path: Path
    input_shape: tuple
    epochs: int
    batch_size: int
    validation_split: float
    learning_rate: float


@dataclass(frozen=True)
class ModelEvaluationConfig:
    root_dir: Path
    test_data_path: Path
    model_path: Path
    metric_file_name: Path
    mlflow_uri: str
    batch_size: int
    target_metric: str
    all_params: dict  
