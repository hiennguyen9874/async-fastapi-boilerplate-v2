#! /usr/bin/env bash
set -e

# Let the DB start
python /app/app/worker_pre_start.py

celery -A app.worker worker --loglevel=INFO -Q default,priority_high --concurrency ${CELERY_CONCURRENCY}
