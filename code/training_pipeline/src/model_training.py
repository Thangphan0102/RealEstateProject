import os
import uuid

import mlflow
from mlflow.models.signature import infer_signature
from mlflow.tracking import MlflowClient

from sklearn.linear_model import ElasticNet

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
    
    def log_metadata(self):
        pass
        

class SklearnTrainer(BaseTrainer):
    def __init__(self) -> None:
        super().__init__()
        
    def train(self):
        train_x, train_y = super().load_data()
        model = ElasticNet(random_state=config.random_seed)
        
        trained_model = super().train(model, train_x, train_y)
        self.log_metadata(trained_model, train_x)
        
        mlflow.end_run()

    def log_metadata(self, model, train_x):
        mlflow.set_tag("mlflow.runName", str(uuid.uuid1())[:8])
        mlflow.log_param("alpha", 0.5)
        mlflow.log_param("l1_ratio", 0.1)
        signature = infer_signature(train_x, model.predict(train_x))
        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path=AppConst.MLFLOW_MODEL_PATH_PREFIX,
            signature=signature
        )
    

class XGBTrainer(BaseTrainer):
    def __init__(self) -> None:
        super().__init__()
    
    def train(self):
        super().train()
        
        
class LGBMTrainer(BaseTrainer):
    def __init__(self) -> None:
        super().__init__()

    def train(self):
        super().train()
        


if __name__ == "__main__":
    trainer = SklearnTrainer()
    trainer.train()
        