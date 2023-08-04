import bentoml
import mlflow
from mlflow.models.signature import ModelSignature

from utils import *

logger = Log(AppConst.BENTOML_SERVICE).log
AppPath()
config = Config()


def save_model() -> bentoml.Model:
    """Read registered_model_version.json from artifacts to get model name, model version, etc. and save
    to bentoml

    Returns:
        bentoml.Model: Saved model
    """
    # Start
    logger.info("Started: save_model")
    
    # Read registered_model_version.json
    registered_model_file = config.registered_model_file
    logger.info(f"Loaded registered_model_file: {registered_model_file}")
    registered_model_dict = load_json(registered_model_file)
    logger.info(f"Loaded registered_model_dict: {registered_model_dict}")
    registered_model = registered_model_dict["register_models"][0]
    
    # Extract model information
    run_id = registered_model["_run_id"]
    model_name = registered_model["_name"]
    model_version = registered_model["_version"]
    model_uri = registered_model["_source"]
    
    # Load mlflow model
    mlflow.set_tracking_uri(config.mlflow_tracking_uri)
    mlflow_model = mlflow.pyfunc.load_model(model_uri=model_uri)
    logger.info(f"Loaded model dict: {mlflow_model.__dict__}")
    model = mlflow_model._model_impl.xgb_model
    model_signature: ModelSignature = mlflow_model.metadata.signature
    
    # Construct feature list
    feature_list = []
    for input_name in model_signature.inputs.input_names():
        feature_list.append(input_name)
    
    # Save model to bentoml
    bentoml_model = bentoml.xgboost.save_model(
        name=model_name,
        model=model,
        signatures={
            "predict": {
                "batchable": False,
            },
        },
        labels={
            "owner": "thangphan",
        },
        metadata={
            "mlflow_run_id": run_id,
            "mlflow_model_name": model_name,
            "mlflow_model_version": model_version,
        },
        custom_objects={
            "feature_list": feature_list,
        },
    )
    logger.info(f"Saved bentoml model dict: {bentoml_model.__dict__}")
    
    # End
    logger.info("Finished: save_model")


if __name__ == "__main__":
    save_model()