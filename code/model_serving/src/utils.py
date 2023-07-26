import os
import sys
import json
import logging
from pathlib import Path

import numpy as np
import pandas as pd
from dotenv import load_dotenv
load_dotenv()


class AppConst:
    LOG_LEVEL = logging.DEBUG
    DATA_EXTRACTION = "data_extraction"
    

class AppPath:
    MODEL_SERVING_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ROOT_DIR = os.path.dirname(os.path.dirname(MODEL_SERVING_DIR))
    
    DATA_SOURCE_DIR = Path(ROOT_DIR, "data_sources")
    FEATURE_STORE_REPO = Path(ROOT_DIR, "feature_repo")
    
    ARTIFACTS_DIR = Path(MODEL_SERVING_DIR, "artifacts")
    BATCH_INPUT_PQ = Path(ARTIFACTS_DIR, "batch_input.parquet")
    BATCH_OUTPUT_PQ = Path(ARTIFACTS_DIR, "batch_output.parquet")
    
    def __init__(self) -> None:
        AppPath.ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
        

class Config:
    def __init__(self) -> None:
        self.feature_dict = {
            "area": np.float64,
            "width": np.float64,
            "length": np.float64,
            "num_bedrooms": np.float64,
            "num_bathrooms": np.float64,
            "district": object,
            "city": object,
            "price": np.float64,
            "legal_document": pd.CategoricalDtype(
                categories=[
                    'Giấy tờ hợp lệ',
                    'Sổ hồng',
                    'Sổ đỏ',
                    'Hợp đồng mua bán',
                    'Không xác định',
                    'Giấy tờ viết tay'
                ],
                ordered=False
            )
        }
        
        self.mlflow_tracking_uri = os.getenv("MLFLOW_TRACKING_URI")
        self.batch_input_file = Path(AppPath.MODEL_SERVING_DIR, os.getenv("BATCH_INPUT_FILE"))
        
    
class Log:
    log: logging.Logger = None
    
    def __init__(self, name="") -> None:
        if Log.log is None:
            Log.log = self._init_logger(name)
            
    def _init_logger(self, name) -> logging.Logger:
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