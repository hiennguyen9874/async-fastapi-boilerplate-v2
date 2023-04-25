#! /usr/bin/env bash

# Let the DB start
echo "backend pre-start..."
python /app/app/backend_pre_start.py
echo "done backend pre-start!"

# Run migrations
alembic upgrade head

# Create initial data in DB
echo "backend init-data..."
python /app/app/initial_data.py
echo "done backend init-data!"
