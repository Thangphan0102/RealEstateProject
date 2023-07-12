from sklearn.model_selection import train_test_split

from utils import *

AppPath()


def main():
    # Start
    logger = Log(AppConst.DATA_PREPARATION).log
    logger.info("Started: Preparing data...")
    
    # Load config
    config = Config()
    logger.info(f"Loaded config: {config.__dict__}")
    
    # Read data
    df = read_parquet(AppPath.TRAINING_PQ)
    X = df.drop([config.target_col], axis=1)
    y = df.loc[:, [config.target_col]]
    
    # Train test split
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=config.test_size,
        random_state=config.random_seed
    )
    
    # Save to files
    train_test_to_parquet(X_train, X_test, y_train, y_test)
    
    # Inspect directory
    inspect_dir(AppPath.TRAIN_X_PQ.parent)
    
    # End
    logger.info("Finished: Preparing data")
    
    
if __name__ == "__main__":
    main()