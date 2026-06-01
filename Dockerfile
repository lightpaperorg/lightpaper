FROM python:3.12-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Build the React IDE frontend
FROM node:22-slim AS frontend

WORKDIR /ide
COPY app/ide/package.json app/ide/package-lock.json ./
RUN npm ci --no-audit
COPY app/ide/ ./
RUN npm run build

FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 libpango-1.0-0 libpangocairo-1.0-0 libpangoft2-1.0-0 \
    libcairo2 libgdk-pixbuf-2.0-0 libffi-dev libglib2.0-0 \
    fonts-liberation && \
    rm -rf /var/lib/apt/lists/* && \
    useradd --create-home appuser

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY . .

# Copy built React app into the right place
COPY --from=frontend /ide/dist app/ide/dist/

RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8080

CMD ["gunicorn", "app.main:app", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--workers", "2", \
     "--bind", "0.0.0.0:8080", \
     "--timeout", "120", \
     "--access-logfile", "-"]
