#!/bin/bash
# Startup script for Railway deployment
# Runs migrations and creates dummy data before starting the server

set -e  # Exit on error

cd /app/backend

echo "Running database migrations..."
python3 manage.py migrate --noinput

echo "Creating dummy data (if needed)..."
python3 manage.py create_dummy_data || echo "Dummy data creation skipped (may already exist)"

echo "Starting Gunicorn server..."
exec python3 -m gunicorn pos_system.wsgi:application --bind 0.0.0.0:${PORT:-8080}

