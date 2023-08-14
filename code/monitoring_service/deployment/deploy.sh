#!/bin/bash

cmd=$1

# constants
DOCKER_USER="$DOCKER_USER"
PROJECT="real_estate"
IMAGE_NAME="monitoring_service"
IMAGE_TAG=$(git describe --always)

if [[ -z "$DOCKER_USER" ]]; then
    echo "Missing \$DOCKER_USER env var"
    exit 1
fi

usage() {
    echo "deploy.sh <command>"
    echo "Available commands:"
    echo " build                build image"
    echo " push                 push image"
    echo " build_push           build and push image"
    echo " dags               deploy airflow dags"
}

if [[ -z "$cmd" ]]; then
    echo "Missing command"
    usage
    exit 1
fi

build() {
    docker build --tag $DOCKER_USER/$PROJECT/$IMAGE_NAME:$IMAGE_TAG -f deployment/Dockerfile .
    docker tag $DOCKER_USER/$PROJECT/$IMAGE_NAME:$IMAGE_TAG $DOCKER_USER/$PROJECT/$IMAGE_NAME:latest
}

push() {
    docker push $DOCKER_USER/$PROJECT/$IMAGE_NAME:$IMAGE_TAG
    docker push $DOCKER_USER/$PROJECT/$IMAGE_NAME:latest
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

shift

case $cmd in
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
    *)
        echo -n "Unknown command: $cmd"
        usage
        exit 1
        ;;
esac
