# ───── base image ──────────────────────────────────────────────
FROM python:3.10-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# ───── system deps ─────────────────────────────────────────────
# --no-install-recommends keeps the image small; cleaning apt cache
# in the same layer avoids dangling files
RUN apt-get update \
 && apt-get install -y --no-install-recommends gcc libpq-dev ffmpeg \
 && rm -rf /var/lib/apt/lists/*

# ───── python deps ─────────────────────────────────────────────
COPY requirements.txt .
RUN python -m pip install --upgrade pip wheel \
 && python -m pip install -r requirements.txt

# ───── project ────────────────────────────────────────────────
COPY . .

EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
