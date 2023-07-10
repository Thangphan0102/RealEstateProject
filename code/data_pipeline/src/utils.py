import os
import sys
from pathlib import Path
import logging

from dotenv import load_dotenv
load_dotenv()


class AppConst:
    INGEST = "ingest"
    CLEAN = "clean"
    EXPLORATION = "exploration"
    

class AppPath:
    # Directories
    ROOT_DIR = os.getenv("ROOT_DIR")
    CODE_DIR = Path(ROOT_DIR, "code")
    DATA_PIPELINE_DIR = Path(CODE_DIR, "data_pipeline")
    DATA_DIR = Path(ROOT_DIR, "data")
    DATA_SOURCE_DIR = Path(DATA_PIPELINE_DIR, "data_source")
    
    # Files
    DATA_FILE_PATH = Path(DATA_SOURCE_DIR, "data.parquet")
    CLEAN_DATA_FILE_PATH = Path(DATA_SOURCE_DIR, "clean_data.parquet")
    
    def __init__(self) -> None:
        AppPath.DATA_SOURCE_DIR.mkdir(parents=True, exist_ok=True)
        

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
        logger.setLevel(logging.INFO)
        return logger