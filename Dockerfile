# ─── base image ────────────────────────────────────────────────────
FROM python:3.12-slim

# hadolint ignore=DL3013
ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FLASK_ENV=production

# ─── system deps ───────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential \
    && rm -rf /var/lib/apt/lists/*

# ─── app code ──────────────────────────────────────────────────────
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

# ─── gunicorn entrypoint ───────────────────────────────────────────
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]
