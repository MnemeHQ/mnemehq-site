# Dockerfile for Mneme Architecture Audit FastAPI Backend
# Multi-stage build for smaller production image
# Build from repository root: docker build -f audit/backend/Dockerfile .

# Build stage
FROM python:3.12-slim AS builder

# Install system dependencies needed for building
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY audit/backend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.12-slim AS production

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create non-root user
RUN groupadd -r mneme && useradd -r -g mneme -d /app -s /sbin/nologin mneme

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=mneme:mneme audit/backend/app/ ./app/

# Copy test fixtures for testing
COPY --chown=mneme:mneme tests/ ./tests/

# Create temp directory for uploads/clones with proper permissions
RUN mkdir -p /tmp/mneme-audit && chown mneme:mneme /tmp/mneme-audit

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    ALLOWED_ORIGINS="http://localhost:3001,http://127.0.0.1:3001" \
    PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

# Switch to non-root user
USER mneme

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health', timeout=5).raise_for_status()" || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]