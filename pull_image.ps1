# PowerShell Script to pull the Ollama Docker image
# This pulls the specific version required for the service

Write-Host "Pulling Ollama Docker image: ollama/ollama:0.13.5"

docker pull ollama/ollama:0.13.5

if ($LASTEXITCODE -eq 0) {
    Write-Host "Successfully pulled ollama/ollama:0.13.5" -ForegroundColor Green
} else {
    Write-Host "Failed to pull the Ollama image" -ForegroundColor Red
    exit 1
}

Write-Host "Image pull completed!" -ForegroundColor Green