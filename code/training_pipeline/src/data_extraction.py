from feast import FeatureStore

from utils import *

logger = Log(AppConst.DATA_EXTRACTION).log
AppPath()


def main():
    # Start
    logger.info("Started: Extracting data...")
    
    # Inspect data source directory
    inspect_dir(AppPath.DATA_SOURCE_DIR)
    
    # Initialize FeatureStore object
    fs = FeatureStore(repo_path=AppPath.FEATURE_STORE_REPO)
    
    # Read entity data
    entity_df = read_parquet(AppPath.ENTITY_PQ)
    
    # Retrieve feature data
    training_df = fs.get_historical_features(
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
    
    # Drop unecessary columns for training
    training_df = training_df.drop(["date_posted", "property_id"], axis=1)
    
    # Log
    logger.info(f"---- Feature schema ----")
    logger.info(training_df.info())
    
    logger.info(f"---- Example features ----\n{training_df.head()}")
    
    # Store as file
    to_parquet(training_df, AppPath.TRAINING_PQ)
    inspect_dir(AppPath.TRAINING_PQ.parent)
    
    # End
    logger.info("Finished: Extracting data")
    
    
if __name__ == "__main__":
    main()
