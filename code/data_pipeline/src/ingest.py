from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()

import pandas as pd

from utils import *
AppPath()


def main():
    # Start
    logger = Log(AppConst.INGEST).log
    logger.info("Started: Ingesting...")
    
    # Read data
    data = []
    for directory in os.listdir(AppPath.DATA_DIR):
        for file in os.listdir(Path(AppPath.DATA_DIR, directory)):
            df = pd.read_json(Path(AppPath.DATA_DIR, directory, file), orient='records', lines=True)
            data.append(df)
    data = pd.concat(data)
    logger.info(f"Loaded {len(data)} data points")
    
    # Store as parquet file
    logger.info("Writing to parquet file...")
    to_parquet(data, AppPath.DATA_PQ)
    
    # End
    if Path(AppPath.DATA_PQ).is_file():
        logger.info(f"Successfully created {AppPath.DATA_PQ}")
    else:
        logger.error(f"Failed creating the data file")

    
if __name__ == "__main__":
    main()