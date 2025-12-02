# Multi-Annotator Conflict Detection System
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY conflict_detector.py .
COPY run_analysis.py .
COPY test_conflict_detector.py .

# Copy dataset
COPY tickets_label.jsonl .

# Set default command
CMD ["python", "run_analysis.py"]
