import uuid
import numpy as np

import mlflow
from mlflow.models.signature import infer_signature, ModelSignature
from mlflow.tracking import MlflowClient

from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.base import BaseEstimator
from xgboost import XGBModel
from lightgbm import LGBMModel

from utils import *

logger = Log(AppConst.MODEL_TRAINING).log
AppPath()
config = Config()
logger.info(f"Loaded config: {config.__dict__}")


class BaseTrainer:
    def __init__(self) -> None:
        self.trainer_name = self.__class__.__name__
        logger.info(f"Initialized: {self.trainer_name}")
        self.set_up_mlflow()
        
        return self
    
    def set_up_mlflow(self):
        mlflow.set_tracking_uri(config.mlflow_tracking_uri)
        mlflow.set_experiment(config.experiment_name)
        logger.info(f"Set tracking URI: {mlflow.get_tracking_uri()}")
        logger.info(f"Mlflow artifact URI: {mlflow.get_artifact_uri()}")
    
    def load_data(self):
        train_x = read_parquet(AppPath.TRAIN_X_PQ)
        train_x = train_x.drop(columns=['district', 'city', 'legal_document'])
        logger.info(f"Loaded training features with shape {train_x.shape}")
        train_y = read_parquet(AppPath.TRAIN_Y_PQ)
        logger.info(f"Loaded training targets with shape {train_y.shape}")
        
        assert len(train_x.shape) == len(train_y.shape), "Length of train_x and train_y should be the same"
        
        return train_x, train_y
    
    def train(self, model, train_x, train_y):
        logger.info(f"Training: {self.trainer_name}")
        model.fit(train_x, train_y)
        logger.info(f"Finished training: {self.trainer_name}")
        
        return model
    
    def evaluate_train_metrics(self, model, train_x, train_y):
        logger.info("Started: Evaluating training metrics")
        pred_y = model.predict(train_x)
        r2 = r2_score(train_y, pred_y)
        mae = mean_absolute_error(train_y, pred_y)
        mse = mean_squared_error(train_y, pred_y)
        rmse = np.sqrt(mse)
        
        return {
            "train_r2_score": r2,
            "train_mae": mae,
            "train_mse": mse,
            "train_rmse": rmse
        }
    
    def log_metadata(self, model, train_metrics):
        mlflow.set_tag("mlflow.runName", str(uuid.uuid1())[:8])
        mlflow.set_tag('estimator_name', model.__class__.__name__)
        mlflow.set_tag('estimator_class', model.__class__.__module__ + "." + model.__class__.__name__)
        
        for key, value in train_metrics.items():
            mlflow.log_metric(key, value)
    
    def save_run_id(self, run_id):
        run_info = RunInfo(run_id)
        run_info.save()
        logger.info(f"Saved run info into {run_info.path}")
        inspect_dir(run_info.path)
    
    def fetch_logged_data(self, run_id):
        client = MlflowClient()
        data = client.get_run(run_id).data
        tags = {k: v for k, v in data.tags.items() if not k.startswith("mlflow.")}
        artifacts = [f.path for f in client.list_artifacts(run_id, "model")]
        logged_data = {
            "params": data.params,
            "metrics": data.metrics,
            "tags": tags,
            "artifacts": artifacts
        }
        logger.info(f"Logged data and model in run '{run_id}'")
        for key, data in logged_data.items():
            logger.info(f"===== Logged {key} =====")
            logger.info(data)
    

class SklearnTrainer(BaseTrainer):
    def __init__(self, model: BaseEstimator, params: dict):
        super().__init__()
        
        self.model = model
        self.trained_model = None
        self.params = params
        self.model.set_params(**self.params)
        
    def train(self):
        # Prepare data
        train_x, train_y = super().load_data()
        
        # Train model
        self.trained_model = super().train(self.model, train_x, train_y)
        
        # Evaluate train metrics
        pred_y = self.trained_model.predict(train_x)
        train_metrics = evaluate_metrics(train_y, pred_y, prefix="train")
        
        # Log metadata
        signature = infer_signature(train_x, self.trained_model.predict(train_x))
        self.log_metadata(signature, train_metrics)

        # End run
        mlflow.end_run()
                
        # Save run_id to json
        run_id = mlflow.last_active_run().info.run_id
        self.save_run_id(run_id)
        
        # Inspect metadata
        self.fetch_logged_data(run_id)
        
    def log_metadata(self, signature: ModelSignature, train_metrics: dict) -> None:
        super().log_metadata(self.trained_model, train_metrics)
        
        mlflow.log_params(self.trained_model.get_params(deep=True))
        mlflow.sklearn.log_model(
            sk_model=self.trained_model,
            artifact_path=AppConst.MLFLOW_MODEL_PATH_PREFIX,
            signature=signature
        )
    

class XGBTrainer(BaseTrainer):
    def __init__(self, model: XGBModel, params: dict):
        super().__init__()

        self.model = model
        self.trained_model = None
        self.params = params
        self.model.set_params(**self.params)
        
    def train(self):
        # Prepare data
        train_x, train_y = super().load_data()
        
        # Train model
        self.trained_model = super().train(self.model, train_x, train_y)
        
        # Evaluate train metrics
        pred_y = self.trained_model.predict(train_x)
        train_metrics = evaluate_metrics(train_y, pred_y, prefix="train")
        
        # Log metadata
        signature = infer_signature(train_x, self.trained_model.predict(train_x))
        self.log_metadata(signature, train_metrics)
        
        # End run
        mlflow.end_run()
        
        # Save run_id to json
        run_id = mlflow.last_active_run().info.run_id
        self.save_run_id(run_id)
        
        # Inspect metadata
        self.fetch_logged_data(run_id)
        
    def log_metadata(self, signature: ModelSignature, train_metrics: dict) -> None:
        super().log_metadata(self.trained_model, train_metrics)
    
        mlflow.log_params(self.trained_model.get_params(deep=True))
        mlflow.xgboost.log_model(
            xgb_model=self.trained_model,
            artifact_path=AppConst.MLFLOW_MODEL_PATH_PREFIX,
            signature=signature
        )
        
class LGBMTrainer(BaseTrainer):
    def __init__(self, model: LGBMModel, params: dict) -> None:
        super().__init__()
        
        self.model = model
        self.trained_model = None
        self.params = params
        self.model.set_params(**self.params)

    def train(self):
        # Prepare data
        train_x, train_y = super().load_data()
        
        # Train model
        self.trained_model = super().train(self.model, train_x, train_y)

        # Evaluate train metrics
        pred_y = self.trained_model.predict(train_x)
        train_metrics = evaluate_metrics(train_y, pred_y, prefix="train")
        
        # Log metadata
        signature = infer_signature(train_x, self.trained_model.predict(train_x))
        self.log_metadata(signature, train_metrics)
        
        # End run
        mlflow.end_run()
        
        # Save run_id to json
        run_id = mlflow.last_active_run().info.run_id
        self.save_run_id(run_id)
        
        # Inspect metadata
        self.fetch_logged_data(run_id)
    
    def log_metadata(self, signature: ModelSignature, train_metrics: dict) -> None:
        super().log_metadata(self.trained_model, train_metrics)
        
        mlflow.log_params(self.trained_model.get_params(deep=True))
        mlflow.lightgbm.log_model(
            lgb_model=self.trained_model,
            artifact_path=AppConst.MLFLOW_MODEL_PATH_PREFIX,
            signature=signature
        )
    

if __name__ == "__main__":
    from lightgbm import LGBMRegressor
    
    params = {
        "n_estimators": 2,
        "max_depth": 2
    }
    model = LGBMRegressor()
    trainer = LGBMTrainer(model, params)
    trainer.train()
        