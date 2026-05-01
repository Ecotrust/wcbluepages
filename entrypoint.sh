#!/bin/sh

set -e

echo "Waiting for PostgreSQL..."
while ! pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" > /dev/null 2>&1; do
    sleep 1
done
echo "PostgreSQL is ready!"

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Compiling SCSS files..."
python manage.py compilescss

echo "Collecting static files..."
python manage.py collectstatic --noinput
chmod -R 755 /app/bluepages/static_root

if [ "$1" = "prod" ]; then
    echo "Starting Gunicorn on :8000"
    gunicorn bluepages.wsgi:application --bind 0.0.0.0:8000
elif [ "$1" = "dev" ]; then
    echo "Starting python development server on :8000"
    python manage.py runserver 0.0.0.0:8000
else
    # Default to the passed command if not 'prod' or 'dev'
    exec "$@"
fi