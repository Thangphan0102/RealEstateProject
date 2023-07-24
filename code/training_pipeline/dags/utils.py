from pathlib import Path
import pendulum
from airflow.models import Variable
from docker.types import Mount


class AppConst:
    DOCKER_USER = Variable.get("DOCKER_USER", "thangphan")
    PROJECT = "real_estate"
    IMAGE_NAME = "training_pipeline"
    TAG = "latest"
    
    
class AppPath:
    ROOT_DIR = Path(Variable.get("ROOT_DIR"))
    CODE_DIR = Path(ROOT_DIR, "code")
    
    DATA_PIPELINE_DIR = Path(CODE_DIR, "data_pipeline")
    TRAINING_PIPELINE_DIR = Path(CODE_DIR, "training_pipeline")

    FEATURE_REPO = Path(ROOT_DIR, "feature_repo")
    DATA_SOURCE_DIR = Path(ROOT_DIR, "data_sources")

    ARTIFACTS_DIR = Path(TRAINING_PIPELINE_DIR, "artifacts")
    

class DefaultConfig:
    DEFAULT_DAG_ARGS = {
        "owner": "thangphan",
        "retries": 0,
        "retry_deplay": pendulum.duration(seconds=20)
    }
    
    DEFAULT_DOCKER_OPERATORS_ARGS = {
        "image": f"{AppConst.DOCKER_USER}/{AppConst.PROJECT}/{AppConst.IMAGE_NAME}:{AppConst.TAG}",
        "api_version": "auto",
        "auto_remove": True,
        "mounts": [
            # Feature repo
            Mount(
                source=AppPath.FEATURE_REPO.absolute().as_posix(),
                target="/real_estate/feature_repo",
                type="bind",
            ),
            # Data source
            Mount(
                source=AppPath.DATA_SOURCE_DIR.absolute().as_posix(),
                target="/real_estate/data_sources",
                type="bind"
            ),
            # Artifacts
            Mount(
                source=AppPath.ARTIFACTS_DIR.absolute().as_posix(),
                target="/real_estate/code/training_pipeline/artifacts",
                type="bind"
            )
        ],
        "mount_tmp_dir": False
    }