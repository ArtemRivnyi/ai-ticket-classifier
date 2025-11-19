FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create user and directories
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app /app/logs && \
    chown -R appuser:appuser /app

WORKDIR /app

# Copy requirements
COPY --chown=appuser:appuser requirements.txt requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/api/v1/health || exit 1

# Run with Gunicorn
CMD ["gunicorn", "--config", "gunicorn_config.py", "app:app"]
