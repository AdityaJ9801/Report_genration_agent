FROM python:3.11-slim
WORKDIR /app

RUN apt-get update --fix-missing && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    gcc \
    pango1.0-tools \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libcairo2 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY static/ ./static/

RUN mkdir -p /app/reports

ENV PORT=8006
EXPOSE ${PORT}

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8006", "--workers", "2"]
