import mlflow
from mlflow.client import MlflowClient
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
    
    # Load data
    test_x = read_parquet(AppPath.TEST_X_PQ)
    logger.info(f"Loaded test features with shape {test_x.shape}")
    test_y = read_parquet(AppPath.TEST_Y_PQ)
    logger.info(f"Loaded test targets with shape {test_y.shape}")
    
    eval_results = EvaluationResult({})
    for run_id in run_info.run_ids:
        # Load trained model
        model = mlflow.pyfunc.load_model(
            f"runs:/{run_id}/{AppConst.MLFLOW_MODEL_PATH_PREFIX}"
        )
        logger.info(f"Loaded model {model.__dict__}")
    
        # Evaluation
        pred_y = model.predict(test_x)
        test_metrics = evaluate_metrics(test_y, pred_y, prefix="test")
    
        # Log metadata
        with mlflow.start_run(run_id):
            for key, value in test_metrics.items():
                mlflow.log_metric(key, value)
    
        # Write evaluation result to file
        eval_result = {run_id: test_metrics}
        eval_results.add_eval_result(eval_result)
        logger.info(f"Evaluation result: {eval_result}")
        
    eval_results.save()
    logger.info(f"Saved evaluation result to {eval_results.path}")
    inspect_dir(eval_results.path)
    

if __name__ == "__main__":
    main()
    