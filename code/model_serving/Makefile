SHELL=/bin/bash

ENV_FILE="./deployment/.env"

build_image:
	source ${ENV_FILE} && bash deployment/deploy.sh build

build_push_image:
	source ${ENV_FILE} && bash deployment/deploy.sh build_push

deploy_dags:
	source ${ENV_FILE} && bash deployment/deploy.sh dags

deploy_registered_model:
	source ${ENV_FILE} && bash deployment/deploy.sh model

compose_up:
	source ${ENV_FILE} && bash deployment/deploy.sh compose_up

compose_down:
	source ${ENV_FILE} && bash deployment/deploy.sh compose_down
	