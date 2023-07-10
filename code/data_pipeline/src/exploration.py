from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()

import pandas as pd

from utils import *


def main():
    # Directories
    ROOT_DIR = os.getenv("ROOT_DIR")
    DATA_PIPELINE_DIR = Path(ROOT_DIR, "code", "data_pipeline")
    DATA_SOURCE_DIR = Path(DATA_PIPELINE_DIR, "data_source")
    CLEAN_DATA_PATH = Path(DATA_SOURCE_DIR, "clean_data.parquet")
    
    # Start
    logger = Log().log
    logger.info("Started exploring...")
    
    # Read data
    try: 
        df = pd.read_parquet(CLEAN_DATA_PATH, engine='fastparquet')
    except FileNotFoundError:
        logger.error(f"Couldn't find {CLEAN_DATA_PATH} to read!")
        return
    else:
        logger.info(f"Successfully load data from {CLEAN_DATA_PATH}")
        
    # Data shape
    logger.info(f"The dataset contains {df.shape[0]} rows and {df.shape[1]} columns")
    
    # Data info
    logger.info("Data info:")
    logger.info(f"\n{df.info()}")
    
    # Missing values
    logger.info("Missing values:")
    missing_df = df.isna().sum().to_frame('count')
    missing_df['proportion'] = round(missing_df['count'] / df.shape[0], 3)
    logger.info(f"\n{missing_df}")
    
    # Data statistics
    logger.info("Data statistics")
    logger.info(f"\n{df.describe()}")
    
    
if __name__ == "__main__":
    main()