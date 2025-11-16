# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# system deps often needed for imdbpy (requests is pure python). Keep small.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

ENV PORT=8000

# use shell form so PORT env var expands
ENTRYPOINT ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
EXPOSE 8000
