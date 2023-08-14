from pathlib import Path
import pendulum
from airflow.models import Variable
from docker.types import Mount


class AppConst:
    DOCKER_USER = Variable.get("DOCKER_USER", "thangphan")
    PROJECT = "real_estate"
    IMAGE_NAME = "monitoring_service"
    TAG = "latest"
    
    
class AppPath:
    ROOT_DIR = Path(Variable.get("ROOT_DIR"))
    CODE_DIR = Path(ROOT_DIR, "code")
    
    MONITORING_SERVICE_DIR = Path(CODE_DIR, "monitoring_service")
    
    DATA_DIR = Path(MONITORING_SERVICE_DIR, "data")
    ARTIFACTS_DIR = Path(MONITORING_SERVICE_DIR, "artifacts")
    
    
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
            # Data
            Mount(
                source=AppPath.DATA_DIR.absolute().as_posix(),
                target="/real_estate/code/monitoring_service/data",
                type="bind"
            ),
            # Artifacts
            Mount(
                source=AppPath.ARTIFACTS_DIR.absolute().as_posix(),
                target="/real_estate/code/monitoring_service/artifacts",
                type="bind"
            ),
        ],
        "mount_tmp_dir": True,
    }
            