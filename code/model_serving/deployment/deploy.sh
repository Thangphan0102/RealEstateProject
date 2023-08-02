#!/bin/bash

cmd=$1

# Constants
DOCKER_USER="$DOCKER_USER"
PROJECT="real_estate"
IMAGE_NAME="model_serving"
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
}

if [[ -z "$cmd" ]]; then
    echo "Missing command"
    usage
    exit 1
fi

build() {
    docker build --tag $DOCKER_USER/$PROJECT/$IMAGE_NAME:$IMAGE_TAG -f deployment/Dockerfile .
    docker tag "$DOCKER_USER"/"$PROJECT"/"$IMAGE_NAME":"$IMAGE_TAG" "$DOCKER_USER"/"$PROJECT"/"$IMAGE_NAME":latest
}

push() {
    docker push "$DOCKER_USER"/"$PROJECT"/"$IMAGE_NAME":"$IMAGE_TAG"
    docker push "$DOCKER_USER"/"$PROJECT"/"$IMAGE_NAME":latest
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
    *)
        echo -n "Unknown command: $cmd"
        usage
        exit 1
        ;;
esac
