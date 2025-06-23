#!/bin/bash

# This script stops all running containers defined in docker-compose.yml,
# then rebuilds the images from source and starts the services in detached mode.
#
# The 'set -e' command ensures that the script will exit immediately if any command fails.
set -e

# Ensure the SSL certificate for localhost exists before building.
if [ -f "./nginx/generate-cert.sh" ]; then
    echo "Checking for local SSL certificate..."
    ./nginx/generate-cert.sh
fi

echo "Stopping and removing existing containers..."
docker-compose down

echo "Building and starting new containers in detached mode..."
docker-compose up --build -d

echo "Application has been rebuilt and started successfully."