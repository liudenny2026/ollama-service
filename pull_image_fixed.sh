#!/bin/bash

# Fixed script to pull the Ollama Docker image from Aliyun Container Registry
# This handles the case where specific SHA tag doesn't exist and properly waits for fallback
set -e  # Exit immediately if a command exits with a non-zero status

echo "Pulling image from Aliyun Container Registry..."
echo "Registry: crpi-x8d8kf9cyh6zayx0.cn-chengdu.personal.cr.aliyuncs.com"
echo "Image: crpi-x8d8kf9cyh6zayx0.cn-chengdu.personal.cr.aliyuncs.com/devsecops2026/ollama-server:main-5b89dd3fafbf3903fd2a8d34e353269cab44b637"

IMAGE_TAG=""

# Try SHA tag first, fallback to latest
if timeout 600 docker pull crpi-x8d8kf9cyh6zayx0.cn-chengdu.personal.cr.aliyuncs.com/devsecops2026/ollama-server:main-5b89dd3fafbf3903fd2a8d34e353269cab44b637 2>/dev/null; then
  IMAGE_TAG="main-5b89dd3fafbf3903fd2a8d34e353269cab44b637"
  echo "✓ Pulled image with SHA tag"
  # Only set GITHUB_ENV if running in GitHub Actions environment
  if [ -n "$GITHUB_ENV" ]; then
    echo "IMAGE_TAG=$IMAGE_TAG" >> $GITHUB_ENV
  fi
  echo "Successfully pulled image with tag: $IMAGE_TAG"
else
  echo "SHA tag not found, trying latest tag..."
  if timeout 600 docker pull crpi-x8d8kf9cyh6zayx0.cn-chengdu.personal.cr.aliyuncs.com/devsecops2026/ollama-server:latest; then
    IMAGE_TAG="latest"
    echo "✓ Pulled image with latest tag"
    # Only set GITHUB_ENV if running in GitHub Actions environment
    if [ -n "$GITHUB_ENV" ]; then
      echo "IMAGE_TAG=$IMAGE_TAG" >> $GITHUB_ENV
    fi
    echo "Successfully pulled image with tag: $IMAGE_TAG"
  else
    echo "❌ Failed to pull any image"
    exit 1
  fi
fi

echo "Successfully pulled image with tag: $IMAGE_TAG"