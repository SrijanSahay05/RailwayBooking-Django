#!/bin/sh

# Wait for the database to be ready
if [ "$DATABASE" = "postgres" ]; then
  echo "Waiting for PostgreSQL..."
  while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
    sleep 0.1
  done
  echo "PostgreSQL started"
fi

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn server..."
exec gunicorn dvmtask2.wsgi:application --bind 0.0.0.0:8000 --workers 3
