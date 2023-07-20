import os
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
from utils import *

load_dotenv()
AppPath()


def main():
    # Start
    logger = Log(AppConst.INGEST).log
    logger.info("Started: Ingesting...")
    inspect_dir(AppPath.DATA_SOURCE_DIR)

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
