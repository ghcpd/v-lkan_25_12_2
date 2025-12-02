FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
CMD ["python", "-m", "src.conflict_resolver.main", "tickets_label.jsonl", "conflicts_output.jsonl"]
