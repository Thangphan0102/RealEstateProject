import mlflow
from mlflow.models.signature import ModelSignature

from utils import *

logger = Log(AppConst.BATCH_PREDICTION).log
AppPath()


def main():
    # Start
    logger.info("Started: Batch predicting...")
    
    config = Config()
    logger.info(f"Loaded config: {config.__dict__}")
    
    # Download model
    registered_model_file = config.registered_model_file
    logger.info(f"Loaded registered_model_file: {registered_model_file}")
    registered_model_dict = load_json(registered_model_file)
    logger.info(f"Loaded registered_model_dict: {registered_model_dict}")
    registered_model = registered_model_dict["register_models"][0]
    model_uri = registered_model["_source"]
    
    mlflow.set_tracking_uri(config.mlflow_tracking_uri)
    mlflow_model = mlflow.pyfunc.load_model(model_uri=model_uri)
    logger.info(mlflow_model.__dict__)
    
    # Load data
    batch_df = read_parquet(AppPath.BATCH_INPUT_PQ)
    
    # Restructure features
    model_signature = mlflow_model.metadata.signature
    feature_list = []
    for name in model_signature.inputs.input_names():
        feature_list.append(name)
    logger.info(f"feature_list: {feature_list}")
    
    # 
    for col in feature_list:
        if col not in batch_df.columns:
            batch_df[col] = 0
            batch_df[col] = batch_df[col].astype('int32')
    batch_df = batch_df[feature_list]
    logger.info(f"batch_df: {batch_df}")
    
    # Predict
    preds = mlflow_model.predict(batch_df)
    batch_df["pred"] = preds

    logger.info("---- Example output ----")
    logger.info(batch_df.head())
    
    # Write predictions to file
    to_parquet(batch_df, AppPath.BATCH_OUTPUT_PQ)
    inspect_dir(AppPath.BATCH_OUTPUT_PQ)
    
    # Result
    result_df = read_parquet(AppPath.BATCH_OUTPUT_PQ)
    
    logger.info("---- Prediction ----")
    logger.info(result_df['pred'])
    
    # End 
    logger.info("Finished: Batch prediction")
    

if __name__ == "__main__":
    main()