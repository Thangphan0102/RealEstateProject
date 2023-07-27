import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator

from utils import *


with DAG(
    dag_id="training_dag",
    default_args=DefaultConfig.DEFAULT_DAG_ARGS,
    schedule_interval="@once",
    start_date=pendulum.datetime(2022, 1, 1, tz="UTC"),
    catchup=False,
    tags=["training_pipeline"]
) as dag:
    feature_store_init_task = DockerOperator(
        task_id="feature_store_init_task",
        **DefaultConfig.DEFAULT_DOCKER_OPERATORS_ARGS,
        command="/bin/bash -c 'feast -c ../../feature_repo apply'"
    )
    
    data_extraction_task = DockerOperator(
        task_id="data_extraction_task",
        **DefaultConfig.DEFAULT_DOCKER_OPERATORS_ARGS,
        command="/bin/bash -c 'cd .. && python training_pipeline/src/data_extraction.py'"
    )
    
    data_validation_task = DockerOperator(
        task_id="data_validation_task",
        **DefaultConfig.DEFAULT_DOCKER_OPERATORS_ARGS,
        command="/bin/bash -c 'cd src/ && python data_validation.py'"
    )
    
    data_preparation_task = DockerOperator(
        task_id="data_preparation_task",
        **DefaultConfig.DEFAULT_DOCKER_OPERATORS_ARGS,
        command="/bin/bash -c 'cd src/ && python data_preparation.py'"
    )
    
    model_training_task = DockerOperator(
        task_id="model_training_task",
        **DefaultConfig.DEFAULT_DOCKER_OPERATORS_ARGS,
        command="/bin/bash -c 'cd src/ && python model_training.py'"
    )
    
    model_evaluation_task = DockerOperator(
        task_id="model_evaluation_task",
        **DefaultConfig.DEFAULT_DOCKER_OPERATORS_ARGS,
        command="/bin/bash -c 'cd src/ && python model_evaluation.py'"
    )
    
    model_validation_task = DockerOperator(
        task_id="model_validation_task",
        **DefaultConfig.DEFAULT_DOCKER_OPERATORS_ARGS,
        command="/bin/bash -c 'cd src/ && python model_validation.py'"
    )
    
    (
        feature_store_init_task >>
        data_extraction_task >>
        data_validation_task >> 
        data_preparation_task >> 
        model_training_task >> 
        model_evaluation_task >>
        model_validation_task
    )
    