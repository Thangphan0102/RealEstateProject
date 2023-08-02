from feast import FeatureStore
import pandas as pd

from utils import *

logger = Log(AppConst.DATA_EXTRACTION).log
AppPath()


def main():
    # Start
    logger.info("Started: Extracting data...")
    config = Config()
    logger.info(f"Loaded config: {config.__dict__}")
    
    # Inspect data source directory
    inspect_dir(AppPath.DATA_SOURCE_DIR)
    
    # Initialize FeatureStore object
    fs = FeatureStore(repo_path=AppPath.FEATURE_STORE_REPO)
    
    # Read entity data
    inspect_dir(config.batch_input_file)
    entity_df = pd.read_csv(config.batch_input_file, parse_dates=['date_posted'], dtype={'property_id': object})
    
    # Retrieve feature data
    logger.info("Fetching feature..")
    batch_input_df = fs.get_historical_features(
        entity_df=entity_df,
        features=[
            "properties_fv:area",
            "properties_fv:width",
            "properties_fv:length",
            "properties_fv:num_bedrooms",
            "properties_fv:num_bathrooms",
            # "properties_fv:district",
            # "properties_fv:city",
            # "properties_fv:legal_document"
        ]
    ).to_df()
    
    # Drop unecessary columns
    batch_input_df = batch_input_df.drop(columns=["date_posted"])
    batch_input_df = batch_input_df.set_index('property_id')
    
    # Log
    logger.info(f"---- Feature schema ----")
    logger.info(batch_input_df.info())
    
    logger.info(f"---- Example features ----\n{batch_input_df.head()}")
    
    # Store as file
    to_parquet(batch_input_df, AppPath.BATCH_INPUT_PQ)
    inspect_dir(AppPath.BATCH_INPUT_PQ)
    
    # End
    logger.info("Finished: Extracting data")
    
    
if __name__ == "__main__":
    main()
