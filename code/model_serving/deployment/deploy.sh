#!/bin/bash

cmd=$1

# Constants
DOCKER_USER="$DOCKER_USER"
PROJECT="$PROJECT"
IMAGE_NAME="$IMAGE_NAME"
IMAGE_TAG=$(git describe --always)

if [[ -z "$DOCKER_USER" ]]; then
    echo "Missing \$DOCKER_USER env var"
    exit 1
fi

usage() {
    echo "deploy.sh <command>"
    echo "Available commands:"
    echo " build              build image"
    echo " push               push image"
    echo " build_push         build and push image"
    echo " dags               deploy airflow dags"
    echo " model              deploy registered model"
    echo " compose_up         up docker compose"
    echo " compose_down       down docker compose"
}

if [[ -z "$cmd" ]]; then
    echo "Missing command"
    usage
    exit 1
fi

build() {
    docker build --tag "$DOCKER_USER"/"$PROJECT"_"$IMAGE_NAME":"$IMAGE_TAG" -f deployment/Dockerfile .
    docker tag "$DOCKER_USER"/"$PROJECT"_"$IMAGE_NAME":"$IMAGE_TAG" "$DOCKER_USER"/"$PROJECT"_"$IMAGE_NAME":latest
}

push() {
    docker push "$DOCKER_USER"/"$PROJECT"_"$IMAGE_NAME":"$IMAGE_TAG"
    docker push "$DOCKER_USER"/"$PROJECT"_"$IMAGE_NAME":latest
}

deploy_dags() {
    if [[ -z "$DAGS_DIR" ]]; then
        echo "Missing \$DAGS_DIR env var"
        usage
        exit 1
    fi

    mkdir -p "$DAGS_DIR"
    cp dags/* "$DAGS_DIR"
}

deploy_model() {
    MODEL_TRAIN_FILE="/Users/thangphan/RealEstate/code/training_pipeline/artifacts/registered_model_version.json"

    if [[ -f "$MODEL_TRAIN_FILE" ]]; then
        MODEL_SERVING_FILE="/Users/thangphan/RealEstate/code/model_serving/artifacts/registered_model_version.json"
        cp $MODEL_TRAIN_FILE $MODEL_SERVING_FILE
        if [[ -f "$MODEL_SERVING_FILE" ]]; then
            echo "Successfully deployed model"
        fi
    else
        echo "$MODEL_TRAIN_FILE not exist."
    fi
}

compose_up() {
    docker-compose --env-file ./deployment/.env -f ./deployment/docker-compose.yml up -d
}

compose_down() {
    docker-compose --env-file ./deployment/.env -f ./deployment/docker-compose.yml down
}

shift 

case "$cmd" in
    build)
        build "$@"
        ;;
    push)
        push "$@"
        ;;
    build_push)
        build "$@"
        push "$@"
        ;;
    dags)
        deploy_dags "$@"
        ;;
    model)
        deploy_model "$@"
        ;;
    compose_up)
        compose_up "$@"
        ;;
    compose_down)
        compose_down "$@"
        ;;
    *)
        echo -n "Unknown command: $cmd"
        usage
        exit 1
        ;;
esac
