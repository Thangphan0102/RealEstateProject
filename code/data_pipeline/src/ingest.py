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
    DATA_DIR = Path(ROOT_DIR, "data")
    DATA_SOURCE_DIR = Path(DATA_PIPELINE_DIR, "data_source")
    DATA_SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    DATA_PATH = Path(DATA_SOURCE_DIR, "data.parquet")

    # Start
    logger = Log().log
    logger.info("Started ingesting...")
    
    # Read data
    data = []
    for directory in os.listdir(DATA_DIR):
        for file in os.listdir(Path(DATA_DIR, directory)):
            df = pd.read_json(Path(DATA_DIR, directory, file), orient='records', lines=True)
            data.append(df)
    data = pd.concat(data)
    logger.info(f"Loaded {len(data)} data points")
    
    # Store as parquet file
    logger.info("Writing to parquet file...")
    data.to_parquet(DATA_PATH, engine='fastparquet')
    
    # End
    if Path(DATA_PATH).is_file():
        logger.info(f"Successfully created {DATA_PATH}!")
    else:
        logger.error(f"Failed creating the data file!")

    
if __name__ == "__main__":
    main()