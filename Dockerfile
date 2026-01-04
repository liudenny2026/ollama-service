# Use the official Ollama image
FROM ollama/ollama:0.13.5

# Copy init script
COPY init_ollama.sh /init_ollama.sh
RUN chmod +x /init_ollama.sh

# Install curl for health checks and other utilities
RUN if which apk > /dev/null 2>&1; then \
    apk add --no-cache curl ca-certificates; \
    elif which apt-get > /dev/null 2>&1; then \
    apt-get update && apt-get install -y --no-install-recommends curl ca-certificates && rm -rf /var/lib/apt/lists/*; \
    elif which yum > /dev/null 2>&1; then \
    yum install -y curl ca-certificates && yum clean all; \
    else \
    echo "Unsupported base image"; \
    exit 1; \
    fi

# Set labels for GitLab Container Registry
LABEL maintainer="GitLab Ollama Service" \
      org.opencontainers.image.title="Ollama Service" \
      org.opencontainers.image.description="Ollama service with qwen3:0.6b model pre-downloaded" \
      org.opencontainers.image.version="0.13.5" \
      org.opencontainers.image.source="https://github.com/ollama/ollama" \
      org.opencontainers.image.licenses="MIT"

# Expose the Ollama API port
EXPOSE 11434

# Health check to ensure the service is running
HEALTHCHECK CMD curl -f http://localhost:11434/api/tags || exit 1

# Create a script to properly start Ollama and download the model
RUN echo '#!/bin/bash' > /start_and_download.sh && \
    echo 'set -e' >> /start_and_download.sh && \
    echo '' >> /start_and_download.sh && \
    echo '# Start Ollama service in background' >> /start_and_download.sh && \
    echo 'ollama serve > /var/log/ollama.log 2>&1 &' >> /start_and_download.sh && \
    echo 'OLLAMA_PID=$!' >> /start_and_download.sh && \
    echo '' >> /start_and_download.sh && \
    echo '# Wait for the service to be available' >> /start_and_download.sh && \
    echo 'max_attempts=60' >> /start_and_download.sh && \
    echo 'attempt=1' >> /start_and_download.sh && \
    echo 'while [ $attempt -le $max_attempts ]; do' >> /start_and_download.sh && \
    echo '  if curl -f http://localhost:11434/api/tags > /dev/null 2>&1; then' >> /start_and_download.sh && \
    echo '    echo "Ollama service is ready!"' >> /start_and_download.sh && \
    echo '    break' >> /start_and_download.sh && \
    echo '  else' >> /start_and_download.sh && \
    echo '    echo "Attempt $attempt/$max_attempts: Waiting for Ollama service..."' >> /start_and_download.sh && \
    echo '    sleep 5' >> /start_and_download.sh && \
    echo '    ((attempt++))' >> /start_and_download.sh && \
    echo '  fi' >> /start_and_download.sh && \
    echo 'done' >> /start_and_download.sh && \
    echo '' >> /start_and_download.sh && \
    echo 'if [ $attempt -gt $max_attempts ]; then' >> /start_and_download.sh && \
    echo '  echo "Error: Ollama service did not start within the expected time"' >> /start_and_download.sh && \
    echo '  cat /var/log/ollama.log || true' >> /start_and_download.sh && \
    echo '  exit 1' >> /start_and_download.sh && \
    echo 'fi' >> /start_and_download.sh && \
    echo '' >> /start_and_download.sh && \
    echo '# Download the default model' >> /start_and_download.sh && \
    echo 'echo "Downloading qwen3:0.6b model..."' >> /start_and_download.sh && \
    echo 'ollama pull qwen3:0.6b || echo "Warning: Model download failed"' >> /start_and_download.sh && \
    echo 'echo "Model setup completed"' >> /start_and_download.sh && \
    echo '' >> /start_and_download.sh && \
    echo '# Wait for Ollama process' >> /start_and_download.sh && \
    echo 'wait $OLLAMA_PID' >> /start_and_download.sh && \
    chmod +x /start_and_download.sh

# Create a script for Streamlit model selector
RUN echo '#!/bin/bash' > /start_streamlit.sh && \
    echo '' >> /start_streamlit.sh && \
    echo '# Start Ollama service in background' >> /start_streamlit.sh && \
    echo 'ollama serve > /dev/null 2>&1 &' >> /start_streamlit.sh && \
    echo '' >> /start_streamlit.sh && \
    echo '# Wait for the service to be available' >> /start_streamlit.sh && \
    echo 'max_attempts=30' >> /start_streamlit.sh && \
    echo 'attempt=1' >> /start_streamlit.sh && \
    echo 'while [ $attempt -le $max_attempts ]; do' >> /start_streamlit.sh && \
    echo '  if curl -f http://localhost:11434/api/tags > /dev/null 2>&1; then' >> /start_streamlit.sh && \
    echo '    echo "Ollama service is ready!"' >> /start_streamlit.sh && \
    echo '    break' >> /start_streamlit.sh && \
    echo '  else' >> /start_streamlit.sh && \
    echo '    echo "Attempt $attempt/$max_attempts: Waiting for Ollama service..."' >> /start_streamlit.sh && \
    echo '    sleep 10' >> /start_streamlit.sh && \
    echo '    ((attempt++))' >> /start_streamlit.sh && \
    echo '  fi' >> /start_streamlit.sh && \
    echo 'done' >> /start_streamlit.sh && \
    echo '' >> /start_streamlit.sh && \
    echo 'if [ $attempt -gt $max_attempts ]; then' >> /start_streamlit.sh && \
    echo '  echo "Error: Ollama service did not start within the expected time"' >> /start_streamlit.sh && \
    echo '  exit 1' >> /start_streamlit.sh && \
    echo 'fi' >> /start_streamlit.sh && \
    echo '' >> /start_streamlit.sh && \
    echo '# Download the default model' >> /start_streamlit.sh && \
    echo 'echo "Downloading qwen3:0.6b model..."' >> /start_streamlit.sh && \
    echo 'ollama pull qwen3:0.6b' >> /start_streamlit.sh && \
    echo 'echo "Model download completed"' >> /start_streamlit.sh && \
    echo '' >> /start_streamlit.sh && \
    echo '# Keep the service running - start Streamlit interface on port 8501' >> /start_streamlit.sh && \
    echo 'echo "Starting Streamlit interface..."' >> /start_streamlit.sh && \
    echo 'streamlit run streamlit_model_selector.py --server.port=8501 --server.address=0.0.0.0 &' >> /start_streamlit.sh && \
    echo 'echo "Streamlit interface available on port 8501"' >> /start_streamlit.sh && \
    echo 'tail -f /dev/null' >> /start_streamlit.sh && \
    chmod +x /start_streamlit.sh

# Copy the combined startup script
COPY start_ollama_and_streamlit.sh /start_ollama_and_streamlit.sh
RUN chmod +x /start_ollama_and_streamlit.sh

# Set the correct entrypoint and default command
ENTRYPOINT ["/bin/bash"]
CMD ["/start_ollama_and_streamlit.sh"]