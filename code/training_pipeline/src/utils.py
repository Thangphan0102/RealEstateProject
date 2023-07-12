import os
import json
import logging
import sys
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
load_dotenv()


class AppConst:
    LOG_LEVEL = logging.DEBUG
    DATA_EXTRACTION = "data_extraction"
    DATA_VALIDATION = "data_validation"
    DATA_PREPARATION = "data_preparation"
    

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