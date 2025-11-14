# ==============================================
# Base Stage - Python dependencies
# ==============================================
FROM python:3.11-slim AS base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ==============================================
# Builder Stage - Install Python packages
# ==============================================
FROM base AS builder

WORKDIR /build

# Install uv for faster dependency management
RUN pip install uv

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies to a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN uv pip install --system -r pyproject.toml

# ==============================================
# Runtime Stage - Production image
# ==============================================
FROM base AS runtime

# Add metadata
LABEL maintainer="WhatsApp MCP Project"
LABEL description="FastAPI Backend - Claude AI and MCP integration"
LABEL version="1.0.0"

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Copy application code
COPY app ./app

# Set correct permissions
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Add venv to PATH
ENV PATH="/opt/venv/bin:$PATH"

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
