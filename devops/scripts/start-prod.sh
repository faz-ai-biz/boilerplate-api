#!/bin/bash
set -e

echo "Waiting for database..."
python devops/scripts/wait_for_db.py

echo "Running migrations..."
alembic upgrade head

echo "Seeding database..."
python devops/scripts/seed_db.py

echo "Starting application..."
uvicorn src.main:app --host $HOST --port $PORT
