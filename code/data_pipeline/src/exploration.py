from pathlib import Path
import os
from dotenv import load_dotenv
from feast import FeatureStore
import pandas as pd
from utils import *

load_dotenv()
AppPath()


def main():
    # Start
    logger = Log(AppConst.EXPLORATION).log
    logger.info("Started: Exploring...")
    
    # Inspect data source directory
    inspect_dir(AppPath.DATA_SOURCE_DIR)

    # Initialize FeatureStore object
    fs = FeatureStore(repo_path=AppPath.FEATURE_STORE_REPO)

    # Read entity data
    entity_df = read_parquet(AppPath.ENTITY_PQ)

    # Retrieve feature data
    df = fs.get_historical_features(
        entity_df=entity_df,
        features=[
            "properties_fv:area",
            "properties_fv:width",
            "properties_fv:length",
            "properties_fv:num_bedrooms",
            "properties_fv:num_bathrooms",
            "properties_fv:district",
            "properties_fv:city",
            "properties_fv:legal_document"
        ]
    ).to_df()
        
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
