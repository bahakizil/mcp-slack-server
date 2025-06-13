# Multi-stage build for smaller production image
FROM python:3.12-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.12-slim as production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000
ENV ENVIRONMENT=production
ENV LOG_LEVEL=INFO
ENV PATH="/opt/venv/bin:$PATH"

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set work directory
WORKDIR /app

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy application code
COPY slack_mcp_app/ ./slack_mcp_app/
COPY run_server.py .
COPY run_server_with_ngrok.py .
COPY pyproject.toml .
COPY LICENSE .
COPY README.md .

# Install the package in development mode
RUN pip install -e .

# Create directories for logs and data
RUN mkdir -p /app/logs /app/data && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE ${PORT}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Add labels for better container management
LABEL maintainer="your-email@domain.com"
LABEL version="1.0.0"
LABEL description="Professional Slack MCP Server"
LABEL org.opencontainers.image.source="https://github.com/yourusername/slack-mcp-server"
LABEL org.opencontainers.image.documentation="https://github.com/yourusername/slack-mcp-server#readme"
LABEL org.opencontainers.image.licenses="MIT"

# Use the CLI for better configuration management
CMD ["slack-mcp-server", "--host", "0.0.0.0", "--port", "8000", "--log-level", "INFO"] 