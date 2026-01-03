#!/bin/bash

# Ollama Service Initialization Script
# This script initializes the Ollama service and ensures the default model is available

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print info messages
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

# Function to print warning messages
print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Function to print error messages
print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Wait for Ollama service to be ready
wait_for_ollama() {
    print_info "Waiting for Ollama service to be ready..."
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -sf http://localhost:11434/api/tags > /dev/null 2>&1; then
            print_info "Ollama service is ready!"
            return 0
        else
            print_info "Attempt $attempt/$max_attempts: Ollama service not ready, waiting..."
            sleep 10
            ((attempt++))
        fi
    done
    
    print_error "Ollama service did not become ready within the expected time"
    return 1
}

# Check if a model exists
model_exists() {
    local model_name=$1
    ollama list | grep -q "$model_name"
}

# Pull a model with progress
pull_model() {
    local model_name=$1
    print_info "Pulling model: $model_name"
    
    if ollama pull "$model_name"; then
        print_info "Successfully pulled model: $model_name"
        return 0
    else
        print_error "Failed to pull model: $model_name"
        return 1
    fi
}

# Main execution
print_info "Starting Ollama service initialization..."

# Wait for the service to be available
if ! wait_for_ollama; then
    print_error "Failed to connect to Ollama service"
    exit 1
fi

# Define default models to ensure are available
DEFAULT_MODELS=("qwen3:1.7b")

# Process each default model
for model in "${DEFAULT_MODELS[@]}"; do
    if model_exists "$model"; then
        print_info "Model $model already exists"
    else
        print_info "Downloading model: $model"
        if pull_model "$model"; then
            print_info "Successfully downloaded $model"
        else
            print_error "Failed to download $model"
            exit 1
        fi
    fi
done

print_info "Ollama service initialized successfully!"
print_info "Available models:"
ollama list

# Keep the container running
print_info "Ollama service is running and ready to accept requests..."
tail -f /dev/null