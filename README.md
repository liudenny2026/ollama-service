# Ollama Service

This service provides an Ollama server for use with the LangChain application. It includes functionality to manage models and ensure the service is properly initialized.

## Features

- Runs Ollama server using the official `ollama/ollama:0.13.5` image
- Automatically downloads the `qwen3:1.7b` model on first startup
- Provides a model manager script for adding additional models
- Includes GitLab CI configuration for automated builds

## Files

- `Dockerfile` - Defines the Ollama service container
- `model_manager.py` - Python script to manage Ollama models (list, pull, delete)
- `init_ollama.sh` - Initialization script that runs when the container starts
- `.gitlab-ci.yml` - CI/CD configuration that triggers on model changes
- `requirements.txt` - Python dependencies for the model manager

## Usage

### Running the Service

The service is automatically started as part of the docker-compose setup:

```bash
docker-compose up --build
```

### Managing Models

You can manage models using the model manager script:

```bash
# List available models
python model_manager.py list

# Pull a new model
python model_manager.py pull mistral:latest

# Delete a model
python model_manager.py delete mistral:latest
```

### Adding New Models

To add a new model to the system:

1. Modify the `init_ollama.sh` script to include your desired model
2. Or use the model manager script after the service is running
3. Commit your changes to trigger the CI pipeline

## CI/CD Pipeline

The pipeline will automatically trigger when:

- Files in the `ollama-service/` directory are modified
- The `.gitlab-ci.yml` file is changed
- The `docker-compose.yml` file is modified

This ensures that any model additions or changes are automatically built and tested.