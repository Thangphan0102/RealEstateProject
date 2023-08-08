#!/bin/bash

# Arguments
property_type=$1
first_page=$2
last_page=$3

# Variable
date=$(date '+%Y-%m-%d')
uuid=$(uuidgen)

# Directories
DATA_DIR="/Users/thangphan/RealEstate/data_sources/data"
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
PYTHON_SCRIPT="$SCRIPT_DIR/add_urls_to_redis.py"

# Usage
usage() {
    echo "Usage:"
    echo "  Crawl properties data from mogi.vn for a specific property type and pages"
    echo "      bash run.sh <property_type> <first_page> <last_page>"
    echo ""
    echo "Arguments:"
    echo "  property_type   property type to crawl"
    echo "  first_page      first page to crawl"
    echo "  last_page       last page to crawl"
    echo ""
    echo "Example:"
    echo "  bash run.sh mua-nha-mat-tien-pho 1 10"
    echo ""
    echo "Available property types:"
    echo "  mua-nha-mat-tien-pho"
    echo "  mua-nha-hem-ngo"
    echo "  mua-nha-biet-thu-lien-ke"
    echo "  mua-duong-noi-bo"
    echo "  mua-can-ho-tap-the-cu-xa"
    echo "  mua-can-ho-penthouse"
    echo "  mua-can-ho-chung-cu"
    echo "  mua-can-ho-officetel"
    echo "  mua-can-ho-dich-vu"
}

# Add URLs to crawl
add_urls_to_redis() {
    python $PYTHON_SCRIPT $property_type $first_page $last_page
}

# Activate spider(s)
activate_spider() {
    cd $SCRIPT_DIR
    scrapy crawl mogi_vn -o "$DATA_DIR/$property_type/$date-$uuid.jsonl"
}

if [[ "$1" == "-h" ]] || [[ "$1" == "--help" ]]; then
    usage
    exit 1
fi

if [[ -z "$property_type" ]] || [[ -z "$first_page" ]] || [[ -z "$last_page" ]]; then
    echo "Not enough arguments"
    usage
    exit 1
fi

shift 3

case $property_type in
    "mua-nha-mat-tien-pho" | "mua-nha-hem-ngo" | "mua-nha-biet-thu-lien-ke" | "mua-duong-noi-bo" | "mua-can-ho-tap-the-cu-xa" | "mua-can-ho-penthouse" | "mua-can-ho-chung-cu" | "mua-can-ho-officetel" | "mua-can-ho-dich-vu")
        case $first_page in
            '' | *[!0-9]*)
                echo "First page must be a number";
                usage
                exit 1 
                ;;
            *)
                case $last_page in
                    '' | *[!0-9]*)
                        echo "Last page must be a number";
                        usage
                        exit 1 
                        ;;
                    *)
                        if [[ $first_page -gt $last_page ]]; then
                            echo "First page must be smaller than last page";
                            usage
                            exit 1
                        fi

                        add_urls_to_redis "$@"
                        activate_spider "$@"
                esac
                ;;
        esac
        ;;
    *)
        echo "Unknown property type"
        usage
        exit 1
        ;;
esac