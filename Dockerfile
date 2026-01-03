# Use the official Ollama image
FROM ollama/ollama:0.13.5

# Install curl for health checks
RUN apk add --no-cache curl

# Expose the Ollama API port
EXPOSE 11434

# Health check to ensure the service is running
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:11434/api/tags || exit 1

# Default command to run Ollama server
CMD ["serve"]