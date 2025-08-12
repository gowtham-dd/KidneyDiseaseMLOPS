import os
import cv2
import numpy as np
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
from tqdm import tqdm
from KidneyClassifier.utils.common import *

CLASS_NAMES = ['Cyst', 'Normal', 'Stone', 'Tumor']

class DataPreprocessing:
    def __init__(self, config, data_dir: str):
        self.config = config
        self.data_dir = data_dir
        create_directories([self.config.root_dir])

    def _processed_data_exists(self):
        """Check if processed data already exists"""
        return os.path.exists(self.config.processed_data_file)

    def load_and_preprocess_images(self):
        """Load and preprocess images if processed data doesn't exist"""
        if self._processed_data_exists():
            logger.info(f"Processed data already exists at {self.config.processed_data_file}")
            processed_data = np.load(self.config.processed_data_file)
            return (
                processed_data['X_train'],
                processed_data['X_test'],
                processed_data['y_train'],
                processed_data['y_test']
            )

        logger.info("No existing processed data found. Starting preprocessing...")
        images = []
        labels = []

        for idx, class_name in enumerate(CLASS_NAMES):
            class_path = os.path.join(self.data_dir, class_name)
            if not os.path.exists(class_path):
                raise FileNotFoundError(f"{class_path} not found")

            for img_name in tqdm(os.listdir(class_path), desc=f"Loading {class_name}"):
                if not img_name.lower().endswith(('.jpg', '.jpeg', '.png')):
                    continue
                    
                img_path = os.path.join(class_path, img_name)
                img = cv2.imread(img_path)
                if img is None:
                    continue
                img = cv2.resize(img, (self.config.image_size, self.config.image_size))
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                img = img / 255.0
                images.append(img)
                labels.append(idx)

        X = np.array(images)
        y = np.array(labels)
        
        return self.apply_smote_and_split(X, y)

    def apply_smote_and_split(self, X, y):
        """Apply SMOTE and train-test split if not already processed"""
        if self._processed_data_exists():
            processed_data = np.load(self.config.processed_data_file)
            return (
                processed_data['X_train'],
                processed_data['X_test'],
                processed_data['y_train'],
                processed_data['y_test']
            )

        logger.info("Applying SMOTE and train-test split...")
        X_flat = X.reshape(len(X), -1)
        smote = SMOTE()
        X_resampled, y_resampled = smote.fit_resample(X_flat, y)
        X_resampled = X_resampled.reshape(-1, self.config.image_size, self.config.image_size, 3)

        X_train, X_test, y_train, y_test = train_test_split(
            X_resampled, y_resampled, 
            test_size=0.2, 
            random_state=42
        )

        np.savez_compressed(
            self.config.processed_data_file,
            X_train=X_train,
            X_test=X_test,
            y_train=y_train,
            y_test=y_test
        )
        
        logger.info(f"Saved processed data to {self.config.processed_data_file}")
        return X_train, X_test, y_train, y_test