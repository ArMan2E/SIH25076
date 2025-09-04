#!/usr/bin/env bash
# Simple demo runner (no docker) - for development
set -e
export $(cat .env | xargs) || true

# create DB (sqlite fallback)
python - <<'PY'
from backend.app.models import init_db
init_db()
print("DB initialized.")
PY

# Start uvicorn in background
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 &

echo "Uvicorn started on http://localhost:8000"
echo "Start a celery worker in another terminal: celery -A backend.worker.celery_app.celery worker --loglevel=info"
