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

You can manage models using multiple methods:

**Streamlit Model Selector (Recommended):**
```bash
# Start the Streamlit model selector
streamlit run streamlit_model_selector.py
# Then open the provided URL in your browser (usually http://localhost:8501)

# On Windows, you can also run:
streamlit run streamlit_model_selector.py
```

**Interactive Model Selector:**
```bash
# Run the interactive model selector
python model_selector.py
```

**Model Manager Script:**
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

1. Use the web model selector: `python web_model_selector.py`
2. Or use the interactive model selector: `python model_selector.py`
3. Or modify the `init_ollama.sh` script to include your desired model
4. Or use the model manager script after the service is running
5. Commit your changes to trigger the CI pipeline

The model selectors provide:
- Menu of popular models to choose from
- Option to enter custom model names
- Automatic download from domestic mirrors for faster speeds in China
- Real-time download progress

## CI/CD Pipeline

The pipeline will automatically trigger when:

- Files in the project directory are modified
- The `.gitlab-ci.yml` file is changed
- The `docker-compose.yml` file is modified

This ensures that any model additions or changes are automatically built and tested.

## GitLab Container Registry

The pipeline automatically builds and pushes Docker images to the GitLab Container Registry:

- **Image Name**: `$CI_REGISTRY_IMAGE`
- **Tags**: 
  - Commit SHA: `$CI_COMMIT_SHORT_SHA` (e.g., `sha-abc123de`)
  - Latest: `latest` (for default branch)
  - Branch-specific: `$CI_COMMIT_REF_SLUG` (for merge requests)

### Using the Built Images

After the CI pipeline runs successfully, you can pull the image from the GitLab Container Registry:

```bash
# Login to GitLab Container Registry
docker login $CI_REGISTRY -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD

# Pull the latest image
docker pull $CI_REGISTRY_IMAGE:latest

# Pull an image with specific commit tag
docker pull $CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA
```

### Required GitLab CI Variables

To enable pushing to GitLab Container Registry, configure these CI/CD variables in your GitLab project:

- `CI_REGISTRY_USER`: GitLab registry user (usually set automatically)
- `CI_REGISTRY_PASSWORD`: GitLab registry password/token (usually set automatically)
- `CI_REGISTRY`: GitLab registry URL (usually set automatically)