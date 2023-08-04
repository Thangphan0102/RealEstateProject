from typing import List, Optional, Dict, Any

import bentoml
import mlflow
import numpy as np
import pandas as pd
import requests
from feast import FeatureStore
from bentoml.io import JSON
from mlflow.models.signature import ModelSignature
from pydantic import BaseModel

from utils import *

logger = Log(AppConst.BENTOML_SERVICE).log
AppPath()
pd.set_option("display.max_columns", None)
config = Config()


bentoml_model = bentoml.xgboost.get("xgboost-reg:latest")
feature_list = bentoml_model.custom_objects["feature_list"]
bentoml_runner = bentoml_model.to_runner()
svc = bentoml.Service(bentoml_model.tag.name, runners=[bentoml_runner])
fs = FeatureStore(repo_path=AppPath.FEATURE_STORE_REPO)


def predict(request: np.ndarray) -> np.ndarray:
    logger.info(f"Started: predict")
    result = bentoml_runner.predict.run(request)
    logger.info(f"Result: {result}")
    logger.info(f"Finished: predict")
    
    return result
    
    
class InferenceRequest(BaseModel):
    request_id: str
    features: Dict[str, List[float]]
    

class InferenceResponse(BaseModel):
    prediction: Optional[List[float]]
    error: Optional[str]
    

@svc.api(
    input=JSON(pydantic_model=InferenceRequest),
    output=JSON(pydantic_model=InferenceResponse)
)
def inference(
    request: InferenceRequest,
    ctx: bentoml.Context
) -> Dict[str, Any]:
    """Run inference

    Args:
        request (InferenceRequest): _description_
        ctx (bentoml.Context): _description_

    Returns:
        Dict[str, Any]: _description_
    """
    logger.info("Started: inference")
    response = InferenceResponse()
    try:
        logger.info(f"request: {request}")
        features = request.features
        
        df = pd.DataFrame.from_dict(features)
        logger.info(df)
        input_features = df[feature_list]
        logger.info(f"input_features: {input_features}")
        
        prediction = predict(input_features)
        df["prediction"] = prediction
        logger.info(f"df: {df}")
        
        response.prediction = prediction
        ctx.response.status_code = 200
        
    except Exception as e:
        logger.error(f"Error: {e}")
        response.error = str(e)
        ctx.response.status_code = 500
        
    logger.info(f"response: {response}")
    
    return response
