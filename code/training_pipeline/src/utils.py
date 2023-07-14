import os
import json
import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

from dotenv import load_dotenv
load_dotenv()


class AppConst:
    LOG_LEVEL = logging.DEBUG
    DATA_EXTRACTION = "data_extraction"
    DATA_VALIDATION = "data_validation"
    DATA_PREPARATION = "data_preparation"
    MODEL_TRAINING = "model_training"
    MODEL_EVALUATION = "model_evaluation"
    MLFLOW_MODEL_PATH_PREFIX = "model"
    

class AppPath:
    ROOT_DIR = os.getenv("ROOT_DIR")
    CODE_DIR = Path(ROOT_DIR, "code")
    DATA_PIPELINE_DIR = Path(CODE_DIR, "data_pipeline")
    TRAINING_PIPELINE_DIR = Path(CODE_DIR, "training_pipeline")
    DATA_SOURCE_DIR = Path(DATA_PIPELINE_DIR, "data_sources")
    ARTIFACTS_DIR = Path(TRAINING_PIPELINE_DIR, "artifacts")
    FEATURE_STORE_REPO = Path(DATA_PIPELINE_DIR, "feature_repo")
    
    TRAINING_PQ = Path(ARTIFACTS_DIR, "train_data.parquet")
    TRAIN_X_PQ = Path(ARTIFACTS_DIR, "train_x.parquet")
    TRAIN_Y_PQ = Path(ARTIFACTS_DIR, "train_y.parquet")
    TEST_X_PQ = Path(ARTIFACTS_DIR, "test_x.parquet")
    TEST_Y_PQ = Path(ARTIFACTS_DIR, "test_y.parquet")

    RUN_INFO = Path(ARTIFACTS_DIR, "run_info.json")
    EVALUATION_RESULT = Path(ARTIFACTS_DIR, "evaluation.json")
    
    def __init__(self) -> None:
        AppPath.ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
        
        
class Config:
    def __init__(self) -> None:
        import numpy as np
        
        self.feature_dict = {
            "area": np.float64,
            "width": np.float64,
            "length": np.float64,
            "num_bedrooms": np.float64,
            "num_bathrooms": np.float64,
            "district": object,
            "city": object,
            "legal_document": pd.CategoricalDtype(categories=['Giấy tờ hợp lệ',
                                                              'Sổ hồng',
                                                              'Sổ đỏ',
                                                              'Hợp đồng mua bán',
                                                              'Không xác định',
                                                              'Giấy tờ viết tay'],
                                                  ordered=False),
            "price": np.float64
        }
        
        self.random_seed = 12
        self.test_size= 0.2
        self.target_col = "price"
        
        self.mlflow_tracking_uri = os.getenv("MLFLOW_TRACKING_URI")
        self.experiment_name = "real_estate"
        
class Log:
    log: logging.Logger = None

    def __init__(self, name="") -> None:
        if Log.log == None:
            Log.log = self._init_logger(name)

    def _init_logger(self, name):
        logger = logging.getLogger(name)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
        logger.setLevel(AppConst.LOG_LEVEL)
        return logger
    

class RunInfo:
    def __init__(self, run_id) -> None:
        self.path = AppPath.RUN_INFO
        self.run_id = run_id
        
    def save(self):
        run_info = {
            "run_id": self.run_id
        }
        dump_json(run_info, self.path)
            
    @staticmethod
    def load(path):
        data = load_json(path)
        run_info = RunInfo(data["run_id"])
        
        return run_info
    
    
class EvaluationResult:
    def __init__(self, eval_metrics: dict) -> None:
        self.path = AppPath.EVALUATION_RESULT
        self.eval_metrics = eval_metrics
        
    def __str__(self) -> str:
        return str(self.__dict__)
    
    def save(self):
        dump_json(self.eval_metrics, self.path)
    
    @staticmethod
    def load(path):
        data = load_json(path)
        eval_result = EvaluationResult(
            data
        )
        return eval_result
    
class EvaluationResult:
    def __init__(self, eval_metrics: dict) -> None:
        self.path = AppPath.EVALUATION_RESULT
        self.eval_metrics = eval_metrics
        
    def __str__(self) -> str:
        return str(self.__dict__)
    
    def save(self):
        dump_json(self.eval_metrics, self.path)
    
    @staticmethod
    def load(path):
        data = load_json(path)
        eval_result = EvaluationResult(
            data
        )
        return eval_result
    
    
def inspect_dir(path):
    Log().log.info(f"Started: inspect_dir({path})")
    path = Path(path)
    if not path.exists():
        Log().log.info(f"Path {path} does not exist")
        return
    elif path.is_file():
        Log().log.info(f"Path {path} is file")
        return
    
    paths = os.listdir(path)
    paths = sorted(paths)
    for path in paths:
        Log().log.info(path)
    
    
def inspect_current_dir():
    cwd = os.getcwd()
    Log().log.info(f"Current directory: {cwd}")
    inspect_dir(cwd)
    
    
def read_parquet(path) -> pd.DataFrame:
    Log().log.info(f"Stared: read_parquet {path}")
    df = pd.read_parquet(path, engine="fastparquet")
    return df


def to_parquet(df: pd.DataFrame, path):
    Log().log.info(f"Started: to_parquet {path}")
    df.to_parquet(path, engine="fastparquet")
    

def train_test_to_parquet(X_train, X_test, y_train, y_test):
    Log().log.info(f"Started: train_test_to_parquet")
    to_parquet(X_train, AppPath.TRAIN_X_PQ)
    to_parquet(X_test, AppPath.TEST_X_PQ)
    to_parquet(y_train, AppPath.TRAIN_Y_PQ)
    to_parquet(y_test, AppPath.TEST_Y_PQ)
    
def dump_json(dict_obj: dict, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(dict_obj, f)
        
def load_json(path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    return data

def evaluate_metrics(actual, predict, prefix="train") -> dict:
    Log().log.info(f"Stared: evaluate_metrics [{prefix}]")
    r2 = r2_score(actual, predict)
    mae = mean_absolute_error(actual, predict)
    mse = mean_squared_error(actual, predict)
    rmse = np.sqrt(mse)
    metrics = {
        "r2_score": r2,
        "mae": mae,
        "mse": mse,
        "rmse": rmse
    }
    metrics = dict(zip([prefix + "_" + key for key in metrics.keys()], metrics.values()))
    return metrics