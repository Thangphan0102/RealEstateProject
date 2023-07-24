import os
import sys
from pathlib import Path
import logging

import pandas as pd

from dotenv import load_dotenv
load_dotenv()


class AppConst:
    LOG_LEVEL = logging.DEBUG
    INGEST = "ingest"
    CLEAN = "clean"
    EXPLORATION = "exploration"
    

class AppPath:
    # Directories
    DATA_PIPELINE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ROOT_DIR = os.path.dirname(os.path.dirname(DATA_PIPELINE_DIR))

    FEATURE_STORE_REPO = Path(ROOT_DIR, "feature_repo")
    DATA_SOURCE_DIR = Path(ROOT_DIR, "data_sources")
    DATA_DIR = Path(DATA_SOURCE_DIR, "data")

    # Files
    DATA_PQ = Path(DATA_SOURCE_DIR, "data.parquet")
    FEATURES_PQ = Path(DATA_SOURCE_DIR, "features.parquet")
    ENTITY_PQ = Path(DATA_SOURCE_DIR, "entity.parquet")
    
    def __init__(self) -> None:
        AppPath.DATA_SOURCE_DIR.mkdir(parents=True, exist_ok=True)
        

class Log:
    log: logging.Logger = None

    def __init__(self, name="") -> None:
        if Log.log is None:
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
