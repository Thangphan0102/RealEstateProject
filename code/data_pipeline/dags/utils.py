from pathlib import Path
import pendulum
from airflow.models import Variable
from docker.types import Mount


class AppConst:
    DOCKER_USER = Variable.get("DOCKER_USER", "thangphan")
    PROJECT = "real_estate"
    IMAGE_NAME = "data_pipeline"
    TAG = "latest"


class AppPath:
    DATA_PIPELINE_DIR = Path(Variable.get("DATA_PIPELINE_DIR"))
    FEATURE_REPO = Path(DATA_PIPELINE_DIR, "feature_repo")


class DefaultConfig:
    DEFAULT_DAG_ARGS = {
        "owner": "thangphan",
        "retries": 0,
        "retry_delay": pendulum.duration(seconds=20)
    }

    DEFAULT_DOCKER_OPERATORS_ARGS = {
        "image": f"{AppConst.DOCKER_USER}/{AppConst.PROJECT}/{AppConst.IMAGE_NAME}:{AppConst.TAG}",
        "api_version": "auto",
        "auto_remove": True,
        "mounts": [
            # Feature repo
            Mount(
                source=AppPath.FEATURE_REPO.absolute().as_posix(),
                target="/data_pipeline/feature_repo",
                type="bind",
            ),
        ]
    }
