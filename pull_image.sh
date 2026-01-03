#!/bin/bash

# Script to pull the Ollama Docker image
# This pulls the specific version required for the service

echo "Pulling Ollama Docker image: ollama/ollama:0.13.5"

docker pull ollama/ollama:0.13.5

if [ $? -eq 0 ]; then
    echo "Successfully pulled ollama/ollama:0.13.5"
else
    echo "Failed to pull the Ollama image"
    exit 1
fi

echo "Image pull completed!"