import mlflow
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from utils import *

logger = Log(AppConst.MODEL_EVALUATION).log
AppPath()


def main():
    logger.info("Started: Evaluating model...")
    
    # Get the latest run to evaluate
    run_info = RunInfo.load(AppPath.RUN_INFO)
    logger.info(f"Loaded run_info {run_info.__dict__}")
    
    # Configuration
    config = Config()
    logger.info(f"Loaded config: {config.__dict__}")
    mlflow.set_tracking_uri(config.mlflow_tracking_uri)
    mlflow.set_experiment(config.experiment_name)
    
    # Load trained model
    model = mlflow.pyfunc.load_model(
        f"runs:/{run_info.run_id}/{AppConst.MLFLOW_MODEL_PATH_PREFIX}"
    )
    logger.info(f"Loaded model {model.__dict__}")
    
    # Load data
    test_x = read_parquet(AppPath.TEST_X_PQ)
    test_x = test_x.drop(columns=['district', 'city', 'legal_document'])
    test_y = read_parquet(AppPath.TEST_Y_PQ)
    logger.info(f"Loaded test features with shape {test_x.shape}")
    train_y = read_parquet(AppPath.TRAIN_Y_PQ)
    logger.info(f"Loaded test targets with shape {test_y.shape}")
    
    # Evaluation
    pred_y = model.predict(test_x)
    test_metrics = evaluate_metrics(test_y, pred_y, prefix="test")
    
    # Write evaluation result to file
    eval_result = EvaluationResult(test_metrics)
    logger.info(f"Evaluation result: {eval_result}")
    eval_result.save()
    logger.info(f"Saved evaluation result to {eval_result.path}")
    inspect_dir(eval_result.path)
    

if __name__ == "__main__":
    main()
    