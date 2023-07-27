import mlflow
from utils import *

logger = Log(AppConst.MODEL_VALIDATION).log
AppPath()


def main():
    # Start
    logger.info("Started: Model validating...")
    
    # Load config
    config = Config()
    logger.info(f"Loaded config: {config.__dict__}")
    mlflow.set_tracking_uri(config.mlflow_tracking_uri)
    
    # Load evaluation result
    result_to_register = {}
    eval_results = EvaluationResult.load(AppPath.EVALUATION_RESULT).__dict__
    for run_id, eval_result in eval_results['eval_results'].items():
        logger.info(f"Result from run id {run_id}: {eval_result}")
        if eval_result['test_mae'] < config.test_mae_threshold:
            result_to_register[run_id] = eval_result
            
    register_models = []
    if len(result_to_register) == 0:
        logger.info("Model validation fails, no models satisfied")
        logger.info("Finished: Model validation")
        return
    else:
        logger.info("Model validation succeeds, registering model..")
        for run_id, eval_result in result_to_register.items():
            register_model = mlflow.register_model(
                f"runs:/{run_id}/{AppConst.MLFLOW_MODEL_PATH_PREFIX}",
                config.registered_model_name,
            )
            register_models.append(register_model.__dict__)
        dump_json({"register_models": register_models}, AppPath.REGISTERED_MODEL_VERSION)
        inspect_dir(AppPath.REGISTERED_MODEL_VERSION)
    
    
if __name__ == "__main__":
    main()
    