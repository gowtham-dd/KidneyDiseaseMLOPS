import os
import urllib.request as request
import zipfile
import pandas as pd
from KidneyClassifier import logger
from KidneyClassifier.utils.common import get_size
import gdown
from src.KidneyClassifier.entity.config_entitiy import DataIngestionConfig

class DataIngestion:
    def __init__(self, config: DataIngestionConfig):
        self.config = config

    
    def download_file(self) -> str:
        extracted_dir = self.config.unzipped_data_dir  # path to the unzipped dataset folder

        if os.path.exists(extracted_dir):
            logger.info(f"Dataset folder already exists at {extracted_dir}. Skipping download.")
            return extracted_dir

    # Proceed to download zip and extract
        zip_download_dir = self.config.local_data_file

        logger.info(f"Downloading data from {self.config.source_URL} into {zip_download_dir}")
        filename = gdown.download(url=self.config.source_URL, output=zip_download_dir, quiet=False)

        logger.info(f"Unzipping file {filename}")
        with zipfile.ZipFile(zip_download_dir, 'r') as zip_ref:
            zip_ref.extractall(self.config.unzip_dir)

        logger.info(f"Dataset unzipped to {self.config.unzipped_data_dir}")
        return self.config.unzipped_data_dir

        
    

    def extract_zip_file(self):
      """
      Extracts the zip file into the data directory if not already extracted.
      """
      unzip_path = self.config.unzip_dir

    # Check if unzip_path exists and is not empty
      if os.path.exists(unzip_path) and os.listdir(unzip_path):
        logger.info(f"Data already extracted at {unzip_path}. Skipping extraction.")
        return

      os.makedirs(unzip_path, exist_ok=True)
      logger.info(f"Extracting zip file {self.config.local_data_file} to {unzip_path}")

      with zipfile.ZipFile(self.config.local_data_file, 'r') as zip_ref:
         zip_ref.extractall(unzip_path)

      logger.info(f"Extraction complete.")
