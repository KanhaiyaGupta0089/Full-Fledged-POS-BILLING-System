#!/bin/bash
# Startup script for Railway deployment
# Runs migrations and creates dummy data before starting the server

set -e  # Exit on error

# Change to backend directory (works from /app or /app/backend)
if [ -d "/app/backend" ]; then
    cd /app/backend
elif [ -d "backend" ]; then
    cd backend
fi

echo "=========================================="
echo "Starting Railway deployment..."
echo "Working directory: $(pwd)"
echo "Python version: $(python3 --version)"
echo "=========================================="

echo ""
echo "Step 1: Running database migrations..."
if python3 manage.py migrate --noinput; then
    echo "✓ Migrations completed successfully"
else
    echo "ERROR: Migrations failed!"
    exit 1
fi

echo ""
echo "Step 2: Creating dummy data (if needed)..."
python3 manage.py create_dummy_data || echo "⚠ Dummy data creation skipped (may already exist)"
echo "✓ Dummy data step completed"

echo ""
echo "Step 3: Starting Gunicorn server on port ${PORT:-8080}..."
echo "=========================================="
exec python3 -m gunicorn pos_system.wsgi:application --bind 0.0.0.0:${PORT:-8080}

