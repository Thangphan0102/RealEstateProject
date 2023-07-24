from dotenv import load_dotenv
from utils import *

pd.set_option("display.max_columns", None)
load_dotenv()
AppPath()


def main():
    # Start
    logger = Log(AppConst.EXPLORATION).log
    logger.info("Started: Exploring...")
    
    # Inspect data source directory
    inspect_dir(AppPath.DATA_SOURCE_DIR)

    # Read entity data
    entity_df = read_parquet(AppPath.ENTITY_PQ)

    # Retrieve feature data
    feature_df = read_parquet(AppPath.FEATURES_PQ)
    
    # Join data
    df = entity_df.join(feature_df, rsuffix="_feature")
    df.drop(columns=["property_id_feature", "date_posted_feature"])
    
    # Inspect data shape
    logger.info(f"The dataset contains {df.shape[0]} rows and {df.shape[1]} columns")
    
    # Inspect data info
    logger.info("Data info:")
    logger.info(f"\n{df.info()}")
    
    # Inspect missing values
    logger.info("Missing values:")
    missing_df = df.isna().sum().to_frame('count')
    missing_df['proportion'] = round(missing_df['count'] / df.shape[0], 3)
    logger.info(f"\n{missing_df}")
    
    # Inspect data statistics
    logger.info("Data statistics")
    logger.info(f"\n{df.describe()}")
    
    
if __name__ == "__main__":
    main()
