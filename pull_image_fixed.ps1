# Fixed PowerShell script to pull the Ollama Docker image from Aliyun Container Registry
# This handles the case where specific SHA tag doesn't exist and properly waits for fallback

Write-Host "Pulling image from Aliyun Container Registry..."
Write-Host "Registry: crpi-x8d8kf9cyh6zayx0.cn-chengdu.personal.cr.aliyuncs.com"
Write-Host "Image: crpi-x8d8kf9cyh6zayx0.cn-chengdu.personal.cr.aliyuncs.com/devsecops2026/ollama-server:main-5b89dd3fafbf3903fd2a8d34e353269cab44b637"

$IMAGE_TAG = ""

# Try SHA tag first, fallback to latest
$shaPullResult = docker pull crpi-x8d8kf9cyh6zayx0.cn-chengdu.personal.cr.aliyuncs.com/devsecops2026/ollama-server:main-5b89dd3fafbf3903fd2a8d34e353269cab44b637 2>&1
$shaPullExitCode = $LASTEXITCODE

if ($shaPullExitCode -eq 0) {
    $IMAGE_TAG = "main-5b89dd3fafbf3903fd2a8d34e353269cab44b637"
    Write-Host "✓ Pulled image with SHA tag" -ForegroundColor Green
    
    # Only set GITHUB_ENV if running in GitHub Actions environment
    if (Test-Path env:GITHUB_ENV) {
        Add-Content -Path $env:GITHUB_ENV -Value "IMAGE_TAG=$IMAGE_TAG"
    }
    
    Write-Host "Successfully pulled image with tag: $IMAGE_TAG" -ForegroundColor Green
} else {
    Write-Host "SHA tag not found, trying latest tag..." -ForegroundColor Yellow
    
    $latestPullResult = docker pull crpi-x8d8kf9cyh6zayx0.cn-chengdu.personal.cr.aliyuncs.com/devsecops2026/ollama-server:latest 2>&1
    $latestPullExitCode = $LASTEXITCODE
    
    if ($latestPullExitCode -eq 0) {
        $IMAGE_TAG = "latest"
        Write-Host "✓ Pulled image with latest tag" -ForegroundColor Green
        
        # Only set GITHUB_ENV if running in GitHub Actions environment
        if (Test-Path env:GITHUB_ENV) {
            Add-Content -Path $env:GITHUB_ENV -Value "IMAGE_TAG=$IMAGE_TAG"
        }
        
        Write-Host "Successfully pulled image with tag: $IMAGE_TAG" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to pull any image" -ForegroundColor Red
        exit 1
    }
}

Write-Host "Successfully pulled image with tag: $IMAGE_TAG" -ForegroundColor Green