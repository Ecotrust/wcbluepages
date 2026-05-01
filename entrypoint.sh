#!/bin/sh

set -e

echo "Waiting for PostgreSQL..."
while ! pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" > /dev/null 2>&1; do
    sleep 1
done
echo "PostgreSQL is ready!"

echo "Syncing built JS assets..."
mkdir -p /app/bluepages/app/static/app/js/dist
cp -r /opt/bluepages-js-dist/. /app/bluepages/app/static/app/js/dist/

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Starting python development server on :8000"
python manage.py runserver 0.0.0.0:8000