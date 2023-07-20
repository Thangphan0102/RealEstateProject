#!/bin/bash

service=$1  # Service as the first argument
cmd=$2      # Command as the second argument

# Service names
MLFLOW="mlflow"
AIRFLOW="airflow"
RESTART_SLEEP_SEC=2

usage() {
    echo "Usage:"
    echo "  run.sh <service> <command> [options]"
    echo "Available services:"
    echo "  $MLFLOW"
    echo "  $AIRFLOW"
    echo "Available commands:"
    echo "  up           run container"
    echo "  down         stop and remove container"
    echo "  restart      restart container"
    echo "Available options:"
    echo "  --build      rebuild when up"
    echo "  --volumes    remove volumns when down"
}

get_docker_compose_file() {
    service=$1
    docker_compose_file="$service/$service-docker-compose.yml"
    echo "$docker_compose_file"
}

up() {
    service=$1
    shift
    docker_compose_file=$(get_docker_compose_file $service)

    # Run docker compose
    docker compose -f "$docker_compose_file" up -d "$@"
}

down() {
    service=$1
    shift
    docker_compose_file=$(get_docker_compose_file $service)

    # Stop docker compose
    docker compose -f "$docker_compose_file" down "$@"
}

# MLFLOW
up_mlflow() {
    up "$MLFLOW" "$@"
}

down_mlflow() {
    down "$MLFLOW" "$@"
}

# AIRFLOW
up_airflow() {
    env_file="$AIRFLOW/.env"
    if [[ ! -f "$env_file" ]]; then
        echo -e "AIRFLOW_UID=$(id -u)\nAIRFLOW_GID=0" > "$env_file"
    fi
    up "$AIRFLOW" "$@"
}

down_airflow() {
    down "$AIRFLOW" "$@"
}

if [[ "$1" == "-h" ]]; then
    usage
    exit 0
fi

if [[ -z "$cmd" ]]; then
    echo "Missing command"
    exit 1
fi

if [[ -z "$service" ]]; then
    echo "Missing service"
    exit 1
fi

shift 2

case $cmd in
    up)
        case $service in
            "$MLFLOW")
                up_mlflow "$@"
                ;;
            "$AIRFLOW")
                up_airflow "$@"
                ;;
            *)
                echo "Unknown service"
                usage
                exit 1
                ;;
        esac
        ;;
    down)
        case $service in
            "$MLFLOW")
                down_mlflow "$@"
                ;;
            "$AIRFLOW")
                down_airflow "$@"
                ;;
            *)
                echo "Unknown service"
                usage
                exit 1
                ;;
        esac
        ;;
    restart)
        case $service in
            "$MLFLOW")
                down_mlflow "$@"
                sleep $RESTART_SLEEP_SEC
                up_mlflow "$@"
                ;;
            "$AIRFLOW")
                down_airflow "$@"
                sleep $RESTART_SLEEP_SEC
                up_airflow "$@"
                ;;
            *)
                echo "Unknown service"
                usage
                exit 1
                ;;
        esac
        ;;
    *)
        echo "Unknown command"
        usage
        exit 1
        ;;
esac