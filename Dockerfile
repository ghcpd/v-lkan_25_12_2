# Multi-Annotator Conflict Detection System
# Python 3.9+ base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create output directory
RUN mkdir -p /app/output

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Default command
CMD ["python", "main.py", "--help"]

# Usage examples:
# Build: docker build -t conflict-detector .
# Run: docker run -v $(pwd)/data:/app/data -v $(pwd)/output:/app/output conflict-detector python main.py --input /app/data/tickets_label.jsonl --output /app/output/results.jsonl
# Test: docker run conflict-detector python -m pytest -v
