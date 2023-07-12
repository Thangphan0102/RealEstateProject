from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()

import pandas as pd

from utils import *


def main():
    # Start
    logger = Log(AppConst.EXPLORATION).log
    logger.info("Started: Exploring...")
    
    # Read data
    try: 
        df = pd.read_parquet(AppPath.CLEAN_DATA_FILE_PATH, engine='fastparquet')
    except FileNotFoundError:
        logger.error(f"Couldn't find {AppPath.CLEAN_DATA_FILE_PATH} to read!")
        return
    else:
        logger.info(f"Successfully load data from {AppPath.CLEAN_DATA_FILE_PATH}")
        
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