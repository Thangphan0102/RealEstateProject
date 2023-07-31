import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator

from utils import *


with DAG(
    dag_id="batch_serving_dag",
    default_args=DefaultConfig.DEFAULT_DAG_ARGS,
    schedule_interval="@once",
    start_date=pendulum.datetime(2022, 1, 1, tz="UTC"),
    catchup=False,
    tags=["model_serving"]
) as dag:
    feature_store_init_task = DockerOperator(
        task_id="feature_store_init_task",
        **DefaultConfig.DEFAULT_DOCKER_OPERATORS_ARGS,
        command="/bin/bash -c 'feast -c ../../feature_repo apply'"
    )
    
    data_extraction_task = DockerOperator(
        task_id="data_extraction_task",
        **DefaultConfig.DEFAULT_DOCKER_OPERATORS_ARGS,
        command="/bin/bash -c 'cd .. && python model_serving/src/data_extraction.py'"
    )
    
    batch_prediction_task = DockerOperator(
        task_id="batch_prediction_task",
        **DefaultConfig.DEFAULT_DOCKER_OPERATORS_ARGS,
        command="/bin/bash -c 'cd .. && python model_serving/src/batch_prediction.py'"
    )
    
    (feature_store_init_task >> data_extraction_task >> batch_prediction_task)
    