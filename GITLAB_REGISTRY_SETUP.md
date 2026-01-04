# GitLab Container Registry Setup Guide

This guide explains how to set up and use GitLab Container Registry for the Ollama service.

## Overview

The project is configured to automatically build and push Docker images to GitLab Container Registry when changes are pushed to the repository. The CI/CD pipeline is defined in `.gitlab-ci.yml`.

## Prerequisites

### GitLab CI/CD Variables

To enable pushing to GitLab Container Registry, you need to configure these CI/CD variables in your GitLab project:

1. Go to your GitLab project → Settings → CI/CD → Variables
2. Add the following variables (if not already set by GitLab):

- `CI_REGISTRY_USER` - GitLab registry user (usually set automatically as `$CI_REGISTRY_USER`)
- `CI_REGISTRY_PASSWORD` - GitLab registry password/token (usually set automatically as `$CI_REGISTRY_PASSWORD`)
- `CI_REGISTRY` - GitLab registry URL (usually set automatically as `registry.gitlab.com`)

Most of these variables are automatically set by GitLab, but make sure they're available.

### GitLab Runner

Make sure your GitLab project has a runner configured that supports Docker operations:
- Docker-in-Docker (dind) service
- Docker executor
- Access to Docker daemon

## CI/CD Pipeline Configuration

The `.gitlab-ci.yml` file defines three stages:

1. **build** - Builds the Docker image and pushes it to GitLab Container Registry
2. **test** - Tests the built image to ensure it works correctly
3. **release** - Tags the image as `latest` and creates preview images for merge requests

## Image Naming Convention

- **Registry**: `$CI_REGISTRY` (e.g., `registry.gitlab.com`)
- **Image Path**: `$CI_REGISTRY_IMAGE` (e.g., `registry.gitlab.com/namespace/project/ollama`)
- **Tags**:
  - `{commit-sha}` - Unique tag for each commit (e.g., `abc123d`)
  - `latest` - Points to the latest successful build on default branch
  - `{branch-name}` - For merge requests and feature branches

## Triggering Builds

The pipeline automatically triggers when:

- Files are modified in the repository
- Specifically: `.gitlab-ci.yml`, `Dockerfile`, `docker-compose.yml`, shell scripts, Python files, or `requirements.txt`
- On the default branch (main/master)

## Using the Built Images

### From GitLab Container Registry

After the CI pipeline runs successfully, you can use the image from GitLab Container Registry:

```bash
# Login to GitLab Container Registry
docker login registry.gitlab.com -u <username> -p <token>

# Pull the latest image
docker pull registry.gitlab.com/your-namespace/your-project/ollama:latest

# Pull an image with specific commit tag
docker pull registry.gitlab.com/your-namespace/your-project/ollama:abc123d

# Run the image
docker run -p 11434:11434 registry.gitlab.com/your-namespace/your-project/ollama:latest
```

### Using docker-compose with GitLab Registry

Use the provided `docker-compose-gitlab.yml` file:

```bash
# Set environment variables
export CI_REGISTRY_IMAGE=registry.gitlab.com/your-namespace/your-project/ollama

# Pull and run the image from GitLab Container Registry
docker-compose -f docker-compose-gitlab.yml up -d
```

## Helper Scripts

### Bash Helper Script

Use the provided helper script to work with the GitLab Container Registry:

```bash
# Build and push to GitLab Container Registry
./docker_push_helper.sh build-and-push

# Pull from GitLab Container Registry
./docker_push_helper.sh pull [tag]

# Run image from GitLab Container Registry
./docker_push_helper.sh run [tag] [port]
```

### PowerShell Helper Script

For Windows users:

```powershell
# Build and push to GitLab Container Registry
.\docker_push_helper.ps1 -Action build-and-push

# Pull from GitLab Container Registry
.\docker_push_helper.ps1 -Action pull -Tag latest

# Run image from GitLab Container Registry
.\docker_push_helper.ps1 -Action run -Tag latest -Port 11434
```

## Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Ensure CI/CD variables are correctly set
   - Check that the GitLab runner has access to registry credentials

2. **Docker Build Fails**
   - Verify Dockerfile syntax
   - Check that the GitLab runner has Docker-in-Docker service enabled

3. **Pipeline Times Out**
   - Building and pushing large Docker images can take time
   - Increase timeout values in pipeline configuration if needed

### Pipeline Logs

Check the pipeline logs in GitLab UI:
- Go to your project → CI/CD → Pipelines
- Click on the running/pending pipeline
- View logs for each job to diagnose issues

## Security Considerations

- Store sensitive credentials as protected CI/CD variables
- Use GitLab's built-in variables when possible
- Regularly rotate registry tokens
- Limit access to the container registry to authorized users only

## Advanced Configuration

### Custom Build Arguments

To pass custom build arguments, modify the `.gitlab-ci.yml` file:

```yaml
script:
  - docker build --build-arg CUSTOM_ARG=value -t $DOCKER_IMAGE_NAME .
```

### Multi-Architecture Builds

For multi-architecture support, you can extend the pipeline to use Docker Buildx:

```yaml
build_multi_arch:
  stage: build
  image: docker:24
  services:
    - docker:24-dind
  before_script:
    - docker run --privileged --rm tonistiigi/binfmt --install all
    - echo "$CI_REGISTRY_PASSWORD" | docker login -u "$CI_REGISTRY_USER" --password-stdin $CI_REGISTRY
  script:
    - docker buildx create --name mybuilder --use
    - docker buildx build --platform linux/amd64,linux/arm64 -t $DOCKER_IMAGE_NAME --push .
```

## Best Practices

1. **Tagging Strategy**
   - Use semantic versioning for releases
   - Keep `latest` tag for the most recent stable build
   - Use commit SHAs for traceability

2. **Image Optimization**
   - Minimize Docker image size
   - Remove unnecessary dependencies
   - Use multi-stage builds when possible

3. **Security**
   - Scan images for vulnerabilities
   - Use official base images
   - Regularly update dependencies

This configuration enables seamless integration with GitLab Container Registry for building, storing, and deploying your Ollama service as Docker images.