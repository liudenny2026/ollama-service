#!/bin/bash

# Script to start both Ollama and Streamlit services
set -e

echo "Starting Ollama and Streamlit services..."

# Start Ollama service in background
echo "Starting Ollama service..."
ollama serve > /var/log/ollama.log 2>&1 &
OLLAMA_PID=$!

# Wait for the Ollama service to be available
echo "Waiting for Ollama service to be available..."
max_attempts=60
attempt=1
while [ $attempt -le $max_attempts ]; do
  if curl -f http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "Ollama service is ready!"
    break
  else
    echo "Attempt $attempt/$max_attempts: Waiting for Ollama service..."
    sleep 5
    ((attempt++))
  fi
done

if [ $attempt -gt $max_attempts ]; then
  echo "Error: Ollama service did not start within the expected time"
  cat /var/log/ollama.log || true
  exit 1
fi

# Download the default model
echo "Downloading qwen3:0.6b model..."
ollama pull qwen3:0.6b || echo "Warning: Model download failed"
echo "Model setup completed"

# Start Streamlit interface in background
echo "Starting Streamlit interface on port 8501..."
streamlit run streamlit_model_selector.py --server.port=8501 --server.address=0.0.0.0 &

echo "Both Ollama and Streamlit services are running!"
echo "Ollama API available at: http://localhost:11434"
echo "Streamlit interface available at: http://localhost:8501"

# Keep the container running
wait $OLLAMA_PID