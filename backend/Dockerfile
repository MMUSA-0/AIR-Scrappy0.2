FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl gnupg ca-certificates && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt && \
    python -m playwright install --with-deps chromium

COPY . /app

EXPOSE 8000
CMD ["uvicorn", "app:APP", "--host", "0.0.0.0", "--port", "8000"]
