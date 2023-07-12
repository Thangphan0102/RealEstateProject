import pandas as pd
from utils import *

logger = Log(AppConst.DATA_VALIDATION).log
AppPath()


def main():
    # Start
    logger.info("Started: Validating data...")
    df = read_parquet(AppPath.TRAINING_PQ)
    check_unexpected_features(df)
    check_expected_features(df)
    logger.info("Finished: Validating data")
    

def check_unexpected_features(df: pd.DataFrame):
    logger.info("Started: check_unexpected_features")
    
    # Load config
    config = Config()
    logger.info(f"Loaded config: {config.__dict__}")
    cols = set(df.columns)
    errors = []
    for col in cols:
        if not col in config.feature_dict:
            errors.append(f"feature \"{col}\" is unexpected")
    
    if len(errors) > 0:
        raise Exception(errors)
    
    
def check_expected_features(df: pd.DataFrame):
    logger.info("Started: check_expected_fatures")
    
    # Load config
    config = Config()
    logger.info(f"Loaded config: {config.__dict__}")
    dtypes = dict(df.dtypes)
    logger.info(dtypes)
    errors = []
    for feature in config.feature_dict:
        if not feature in dtypes:
            errors.append(f"feature \"{feature}\" not found")
        else:
            expected_type = config.feature_dict[feature]
            real_type = dtypes[feature]
            if expected_type != real_type:
                errors.append(
                    f"feature \"{feature}\" expects type \"{expected_type}\", but received \"{real_type}\" instead"
                )
                
    if len(errors) > 0:
        raise Exception(errors)
    

if __name__ == "__main__":
    main()