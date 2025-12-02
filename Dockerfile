FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY conflict_detector ./conflict_detector
COPY tickets_label.jsonl ./
COPY pytest.ini ./
COPY tests ./tests
COPY reports ./reports

# Default command
ENTRYPOINT ["python", "-m", "conflict_detector.cli"]
CMD ["--help"]
