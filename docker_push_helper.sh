#!/bin/bash
#
# Helper script to work with GitLab Container Registry
#

set -e

# Configuration
CI_REGISTRY="${CI_REGISTRY:-registry.gitlab.com}"
PROJECT_PATH="${CI_PROJECT_PATH:-$(git remote get-url origin | sed -n 's/.*:\/\/[^\/]*\/\(.*\.git\)$/\1/p' | sed 's/\.git$//')}"
IMAGE_NAME="${CI_REGISTRY}/${PROJECT_PATH}/ollama"

echo "GitLab Container Registry Helper"
echo "================================="
echo "Registry: $CI_REGISTRY"
echo "Project: $PROJECT_PATH"
echo "Image: $IMAGE_NAME"
echo ""

if [ "$1" == "build-and-push" ]; then
    echo "Building and pushing Docker image..."
    echo ""
    
    # Get commit SHA
    COMMIT_SHA=$(git rev-parse --short HEAD)
    echo "Commit SHA: $COMMIT_SHA"
    
    # Build the image
    echo "Building image: $IMAGE_NAME:$COMMIT_SHA"
    docker build -t $IMAGE_NAME:$COMMIT_SHA .
    
    # Tag as latest
    echo "Tagging as latest..."
    docker tag $IMAGE_NAME:$COMMIT_SHA $IMAGE_NAME:latest
    
    # Login to registry (if credentials are available)
    if [ -n "$CI_REGISTRY_USER" ] && [ -n "$CI_REGISTRY_PASSWORD" ]; then
        echo "Logging in to registry..."
        echo $CI_REGISTRY_PASSWORD | docker login $CI_REGISTRY -u $CI_REGISTRY_USER --password-stdin
    else
        echo "Warning: Registry credentials not found in environment variables."
        echo "Please login manually: docker login $CI_REGISTRY"
        echo ""
    fi
    
    # Push images
    echo "Pushing image: $IMAGE_NAME:$COMMIT_SHA"
    docker push $IMAGE_NAME:$COMMIT_SHA
    echo "Pushing image: $IMAGE_NAME:latest"
    docker push $IMAGE_NAME:latest
    
    echo ""
    echo "Successfully pushed images to GitLab Container Registry!"
    echo " - $IMAGE_NAME:$COMMIT_SHA"
    echo " - $IMAGE_NAME:latest"

elif [ "$1" == "pull" ]; then
    TAG="${2:-latest}"
    echo "Pulling image: $IMAGE_NAME:$TAG"
    docker pull $IMAGE_NAME:$TAG
    echo "Successfully pulled $IMAGE_NAME:$TAG"

elif [ "$1" == "run" ]; then
    TAG="${2:-latest}"
    PORT="${3:-11434}"
    echo "Pulling and running image: $IMAGE_NAME:$TAG on port $PORT"
    docker pull $IMAGE_NAME:$TAG
    docker run -d --name ollama-gitlab -p $PORT:11434 -v ollama_data:/root/.ollama $IMAGE_NAME:$TAG
    echo "Ollama service is now running on http://localhost:$PORT"
    echo "Check logs with: docker logs -f ollama-gitlab"

elif [ "$1" == "help" ] || [ "$1" == "-h" ] || [ -z "$1" ]; then
    echo "Usage:"
    echo "  $0 build-and-push    # Build and push Docker image to GitLab Container Registry"
    echo "  $0 pull [tag]        # Pull image from GitLab Container Registry (default: latest)"
    echo "  $0 run [tag] [port]  # Run image from GitLab Container Registry (default: latest, port: 11434)"
    echo "  $0 help              # Show this help"
    echo ""
    echo "Environment variables (if available):"
    echo "  CI_REGISTRY         # Registry URL (default: registry.gitlab.com)"
    echo "  CI_PROJECT_PATH     # Project path (default: extracted from git remote)"
    echo "  CI_REGISTRY_USER    # Registry user"
    echo "  CI_REGISTRY_PASSWORD # Registry password"

else
    echo "Unknown command: $1"
    echo "Run '$0 help' for usage information."
    exit 1
fi