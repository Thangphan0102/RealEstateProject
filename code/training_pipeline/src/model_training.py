import uuid
import numpy as np
from typing import TypedDict

import mlflow
from mlflow.models.signature import infer_signature, ModelSignature
from mlflow.tracking import MlflowClient

from hyperopt import STATUS_OK

from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.base import BaseEstimator
from xgboost import XGBModel
from lightgbm import LGBMModel

from utils import *

logger = Log(AppConst.MODEL_TRAINING).log
AppPath()
RUN_INFO = RunInfo([])
config = Config()
logger.info(f"Loaded config: {config.__dict__}")


def load_data():
    train_x = read_parquet(AppPath.TRAIN_X_PQ)
    logger.info(f"Loaded training features with shape {train_x.shape}")
    train_y = read_parquet(AppPath.TRAIN_Y_PQ)
    logger.info(f"Loaded training targets with shape {train_y.shape}")

    assert len(train_x.shape) == len(train_y.shape), "Lengths of train_x and train_y should be equal"

    return train_x, train_y


def set_up_mlflow():
    mlflow.set_tracking_uri(config.mlflow_tracking_uri)
    experiment = mlflow.set_experiment(config.experiment_name)
    logger.info(f"Set tracking URI: {mlflow.get_tracking_uri()}")
    logger.info(f"Set tracking experiment with name '{experiment.name}' and id '{experiment.experiment_id}'")


def fetch_logged_data(run_id):
    client = MlflowClient()
    data = client.get_run(run_id).data
    tags = {k: v for k, v in data.tags.items() if not k.startswith("mlflow.")}
    artifacts = [f.path for f in client.list_artifacts(run_id, "model")]
    logged_data = {"params": data.params, "metrics": data.metrics, "tags": tags, "artifacts": artifacts}
    logger.info(f"Logged data and model in run '{run_id}'")
    for key, data in logged_data.items():
        logger.info(f"===== Logged {key} =====")
        logger.info(data)


class BaseTrainer:
    def __init__(self, model, params: TypedDict):
        self.trainer_name = self.__class__.__name__
        logger.info(f"Initialized: {self.trainer_name}")

        self.model = model
        self.trained_model = None
        self.params = params

    def train(self, train_x, train_y):
        with mlflow.start_run(nested=True, description="child-run") as run:
            # Set params
            self.model.set_params(**self.params)
            logger.info(f"Model's parameters: {self.model.get_params(deep=True)}")

            # Train
            logger.info(f"Started training: {self.trainer_name}")
            self.trained_model = self.model.fit(train_x, train_y)
            logger.info(f"Finished training: {self.trainer_name}")

            # Evaluate train metrics
            pred_y = self.trained_model.predict(train_x)
            train_metrics = evaluate_metrics(train_y, pred_y, prefix="train")
            loss = train_metrics['train_mse']

            # Log metadata
            signature = infer_signature(train_x, self.trained_model.predict(train_x))
            self.log_metadata(signature, train_metrics)

            # Save run_id
            run_id = run.info.run_id
            RUN_INFO.append(run_id)

            # Inspect metadata
            fetch_logged_data(run_id)

        return loss

    def log_metadata(self, model, train_metrics):
        mlflow.set_tag("mlflow.runName", str(uuid.uuid1())[:8])
        mlflow.set_tag('estimator_name', model.__class__.__name__)
        mlflow.set_tag('estimator_class', model.__class__.__module__ + "." + model.__class__.__name__)

        for key, value in train_metrics.items():
            mlflow.log_metric(key, value)


class SklearnTrainer(BaseTrainer):
    def __init__(self, model: BaseEstimator, params: TypedDict):
        super().__init__(model, params)

    def train(self, **kwargs):
        with mlflow.start_run(nested=True, description="child-run") as run:
            # Train model
            self.trained_model = super().train(train_x, train_y)

            # Evaluate train metrics
            pred_y = self.trained_model.predict(train_x)
            train_metrics = evaluate_metrics(train_y, pred_y, prefix="train")
            loss = train_metrics['train_mse']

            # Log metadata
            signature = infer_signature(train_x, self.trained_model.predict(train_x))
            self.log_metadata(signature, train_metrics)

            # Save run_id
            run_id = run.info.run_id
            RUN_INFO.append(run_id)

            # Inspect metadata
            fetch_logged_data(run_id)

        return loss

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
        super().__init__(model, params)

    def log_metadata(self, signature: ModelSignature, train_metrics: dict) -> None:
        super().log_metadata(self.trained_model, train_metrics)

        mlflow.log_params(self.trained_model.get_params(deep=True))
        mlflow.xgboost.log_model(
            xgb_model=self.trained_model,
            artifact_path=AppConst.MLFLOW_MODEL_PATH_PREFIX,
            signature=signature
        )


class LGBMTrainer(BaseTrainer):
    def __init__(self, model: LGBMModel, params: TypedDict) -> None:
        super().__init__(model, params)

        self.model = model
        self.trained_model = None
        self.params = params
        self.model.set_params(**self.params)

    def train(self, **kwargs):
        # Prepare data
        train_x, train_y = super().load_data()

        # Train model
        self.trained_model = super().train(train_x, train_y)

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
        fetch_logged_data(run_id)

    def log_metadata(self, signature: ModelSignature, train_metrics: dict) -> None:
        super().log_metadata(self.trained_model, train_metrics)

        mlflow.log_params(self.trained_model.get_params(deep=True))
        mlflow.lightgbm.log_model(
            lgb_model=self.trained_model,
            artifact_path=AppConst.MLFLOW_MODEL_PATH_PREFIX,
            signature=signature
        )


if __name__ == "__main__":
    from xgboost import XGBRegressor
    from hyperopt import fmin, tpe, Trials

    set_up_mlflow()

    X_train, y_train = load_data()

    search_space = config.search_space

    trials = Trials()

    def objective(search_space):
        model = XGBRegressor()
        trainer = XGBTrainer(model, search_space)
        loss = trainer.train(X_train, y_train)
        return loss

    with mlflow.start_run(run_name='xgboost_models'):
        best = fmin(
            fn=objective,
            space=search_space,
            algo=tpe.suggest,
            trials=trials,
            max_evals=50,
            rstate=np.random.default_rng(config.random_seed)
        )

    # Save run_ids
    RUN_INFO.save()
    logger.info(f"Saved run info into {RUN_INFO.path}")
    inspect_dir(RUN_INFO.path)
