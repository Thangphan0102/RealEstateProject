import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator

from utils import *

with DAG(
    dag_id="batch_monitoring_dag",
    default_args=DefaultConfig.DEFAULT_DAG_ARGS,
    schedule_interval="@once",
    start_date=pendulum.datetime(2022, 1, 1, tz="UTC"),
    catchup=False,
    tags=["monitoring_service"]
) as dag:
    batch_monitoring_task = DockerOperator(
        task_id="batch_monitoring_task",
        **DefaultConfig.DEFAULT_DOCKER_OPERATORS_ARGS,
        command="/bin/bash -c 'cd .. && python monitoring_service/src/batch_monitoring.py'"
    )
    