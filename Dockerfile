FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY src ./src
COPY tickets_label.jsonl ./tickets_label.jsonl
COPY tests ./tests
ENTRYPOINT ["python", "-m", "tickets_conflict.cli"]
