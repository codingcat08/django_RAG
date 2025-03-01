#!/bin/bash
set -e

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to start..."
while ! nc -z db 5432; do
  sleep 0.5
done
echo "PostgreSQL started"

# Apply database migrations
echo "Applying migrations..."
python manage.py migrate

# Execute the command passed to docker run
exec "$@"