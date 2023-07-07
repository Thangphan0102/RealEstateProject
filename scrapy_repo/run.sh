#!/bin/bash

# Arguments
property_type=$1
first_page=$2
last_page=$3

# Directories
DATA_DIR="/Users/thangphan/RealEstate/data"
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
PYTHON_SCRIPT="$SCRIPT_DIR/add_urls_to_redis.py"

# Add URLs to crawl
run_python_script() {
    python $PYTHON_SCRIPT $property_type $first_page $last_page
}

# Get usage
usage() {
    python $PYTHON_SCRIPT -h
}


# Activate spider(s)
activate_spider() {
    cd $SCRIPT_DIR
    scrapy crawl mogi_vn -o "$DATA_DIR/$property_type/data.jsonl"
}

case "$1" in
"-h")
    usage
    exit 1
    ;;
*)
    run_python_script "$@"
    activate_spider "$@"
    ;;
esac