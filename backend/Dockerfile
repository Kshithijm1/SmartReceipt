# backend/Dockerfile
FROM python:3.11-slim AS base
ENV PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.1

RUN apt-get update && \
    apt-get install -y build-essential git curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY ./app ./app

# Copy Celery entrypoint
COPY celery_app.py .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
