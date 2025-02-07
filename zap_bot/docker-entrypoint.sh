#!/bin/bash
set -e

LOCAL="0"
LOOP="0"

POSITIONAL=()
while [[ $# -gt 0 ]]
do
    key="$1"

    case $key in
        -e|--environment)
        ENVIRONMENT="$2"
        shift # past argument
        shift # past value
        ;;
        -L|--local)
        LOCAL="1"
        shift # past argument
        #shift # past value
        ;;
        -LO|--loop)
        LOOP="1"
        shift # past argument
        #shift # past value
        ;;
        *)    # unknown option
        POSITIONAL+=("$1") # save it in an array for later
        shift # past argument
        ;;
    esac
done

if [ -f "/app/.env" ]; then
    echo "ENV file exists."
    source /app/.env
fi

if [ -z "$ENVIRONMENT" ]; then
    echo "No environment set, using FLASK_DEBUG instead."
    ENVIRONMENT=$FLASK_DEBUG
fi

echo "Environment set: $ENVIRONMENT"

cd /app/zap_bot

echo "Installing dependencies"
pip install --no-cache-dir -r requirements.txt

if [ "$LOCAL" -eq "1" ]; then
    echo 'Starting Python Server'
    flask run --host=0.0.0.0
    exit 0
fi

if [ "$LOOP" -eq "1" ]; then
	echo "Looping"
    while true; do
        sleep 30;
    done
fi
