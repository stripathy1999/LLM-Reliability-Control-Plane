# Backend Dockerfile for Google Cloud Run
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY models/ ./models/

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port (Cloud Run uses PORT env var, defaults to 8080)
EXPOSE 8080

# Cloud Run sets PORT automatically, but we default to 8080
ENV PORT=8080

# Run the application - use PORT from environment (Cloud Run sets this to 8080)
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080} --workers 1

