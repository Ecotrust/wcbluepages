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

echo "Compiling SCSS files..."
python manage.py compilescss

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear
chmod -R 755 /app/bluepages/static_root

if [ "$1" = "prod" ]; then
    echo "Starting Gunicorn on :8000"
    exec gunicorn bluepages.wsgi:application --bind 0.0.0.0:8000
elif [ "$1" = "dev" ]; then
    echo "Starting python development server on :8000"
    exec python manage.py runserver 0.0.0.0:8000
else
    # Default to the passed command if not 'prod' or 'dev'
    exec "$@"
fi