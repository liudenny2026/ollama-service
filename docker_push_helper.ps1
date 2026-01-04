# PowerShell script to work with GitLab Container Registry
param(
    [string]$Action = "help",
    [string]$Tag = "latest",
    [int]$Port = 11434
)

# Configuration
$CI_REGISTRY = if ($env:CI_REGISTRY) { $env:CI_REGISTRY } else { "registry.gitlab.com" }
$PROJECT_PATH = if ($env:CI_PROJECT_PATH) { $env:CI_PROJECT_PATH } else { 
    # Try to get project path from git remote
    $gitRemote = git remote get-url origin 2>$null
    if ($gitRemote) {
        $gitRemote -replace ".*://[^/]*(/.*)\.git$", '$1' -replace "^/", ""
    } else {
        Write-Host "Could not determine project path from git remote" -ForegroundColor Yellow
        ""
    }
}
$IMAGE_NAME = "${CI_REGISTRY}/${PROJECT_PATH}/ollama"

Write-Host "GitLab Container Registry Helper" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green
Write-Host "Registry: $CI_REGISTRY"
Write-Host "Project: $PROJECT_PATH"
Write-Host "Image: $IMAGE_NAME"
Write-Host ""

switch ($Action) {
    "build-and-push" {
        Write-Host "Building and pushing Docker image..." -ForegroundColor Cyan
        Write-Host ""
        
        # Get commit SHA
        $COMMIT_SHA = git rev-parse --short HEAD
        Write-Host "Commit SHA: $COMMIT_SHA"
        
        # Build the image
        Write-Host "Building image: $IMAGE_NAME`:$COMMIT_SHA" -ForegroundColor Cyan
        docker build -t "$IMAGE_NAME`:$COMMIT_SHA" .
        
        # Tag as latest
        Write-Host "Tagging as latest..." -ForegroundColor Cyan
        docker tag "$IMAGE_NAME`:$COMMIT_SHA" "$IMAGE_NAME`:latest"
        
        # Login to registry (if credentials are available)
        if ($env:CI_REGISTRY_USER -and $env:CI_REGISTRY_PASSWORD) {
            Write-Host "Logging in to registry..." -ForegroundColor Cyan
            echo $env:CI_REGISTRY_PASSWORD | docker login $CI_REGISTRY -u $env:CI_REGISTRY_USER --password-stdin
        } else {
            Write-Host "Warning: Registry credentials not found in environment variables." -ForegroundColor Yellow
            Write-Host "Please login manually: docker login $CI_REGISTRY" -ForegroundColor Yellow
            Write-Host ""
        }
        
        # Push images
        Write-Host "Pushing image: $IMAGE_NAME`:$COMMIT_SHA" -ForegroundColor Cyan
        docker push "$IMAGE_NAME`:$COMMIT_SHA"
        Write-Host "Pushing image: $IMAGE_NAME`:latest" -ForegroundColor Cyan
        docker push "$IMAGE_NAME`:latest"
        
        Write-Host ""
        Write-Host "Successfully pushed images to GitLab Container Registry!" -ForegroundColor Green
        Write-Host " - $IMAGE_NAME`:$COMMIT_SHA"
        Write-Host " - $IMAGE_NAME`:latest"
    }

    "pull" {
        Write-Host "Pulling image: $IMAGE_NAME`:$Tag" -ForegroundColor Cyan
        docker pull "$IMAGE_NAME`:$Tag"
        Write-Host "Successfully pulled $IMAGE_NAME`:$Tag" -ForegroundColor Green
    }

    "run" {
        Write-Host "Pulling and running image: $IMAGE_NAME`:$Tag on port $Port" -ForegroundColor Cyan
        docker pull "$IMAGE_NAME`:$Tag"
        docker run -d --name ollama-gitlab -p ${Port}:11434 -v ollama_data:/root/.ollama "$IMAGE_NAME`:$Tag"
        Write-Host "Ollama service is now running on http://localhost:$Port" -ForegroundColor Green
        Write-Host "Check logs with: docker logs -f ollama-gitlab" -ForegroundColor Green
    }

    "list" {
        Write-Host "Listing available images in GitLab Container Registry..." -ForegroundColor Cyan
        Write-Host "To list images, visit: https://${CI_REGISTRY}/v2/${PROJECT_PATH}/" -ForegroundColor Yellow
        Write-Host "Or use: docker search ${CI_REGISTRY}/${PROJECT_PATH}" -ForegroundColor Yellow
    }

    "help" {
        Write-Host "Usage:" -ForegroundColor Green
        Write-Host "  powershell -File $($MyInvocation.MyCommand.Name) -Action build-and-push    # Build and push Docker image to GitLab Container Registry"
        Write-Host "  powershell -File $($MyInvocation.MyCommand.Name) -Action pull -Tag <tag>        # Pull image from GitLab Container Registry (default: latest)"
        Write-Host "  powershell -File $($MyInvocation.MyCommand.Name) -Action run -Tag <tag> -Port <port>  # Run image from GitLab Container Registry (default: latest, port: 11434)"
        Write-Host "  powershell -File $($MyInvocation.MyCommand.Name) -Action list                 # List images in registry"
        Write-Host "  powershell -File $($MyInvocation.MyCommand.Name) -Action help                 # Show this help"
        Write-Host ""
        Write-Host "Environment variables (if available):" -ForegroundColor Green
        Write-Host "  `$env:CI_REGISTRY         # Registry URL (default: registry.gitlab.com)"
        Write-Host "  `$env:CI_PROJECT_PATH     # Project path (default: extracted from git remote)"
        Write-Host "  `$env:CI_REGISTRY_USER    # Registry user"
        Write-Host "  `$env:CI_REGISTRY_PASSWORD # Registry password"
    }

    default {
        Write-Host "Unknown command: $Action" -ForegroundColor Red
        Write-Host "Run 'powershell -File $($MyInvocation.MyCommand.Name) -Action help' for usage information." -ForegroundColor Yellow
    }
}