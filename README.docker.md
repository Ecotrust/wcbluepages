# Docker Setup for WC Bluepages

## Quick Start

### 1. Build and start the containers:

```bash
docker-compose up --build
```

### 2. Run initial setup (first time only):

```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Create a superuser
docker-compose exec web python manage.py createsuperuser

# Load fixtures
docker-compose exec web python manage.py loaddata app/fixtures/initial.json
docker-compose exec web python manage.py loaddata address/fixtures/initial.json

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput
```

### 3. Access the application:

- Web application: http://localhost:8000
- Admin interface: http://localhost:8000/admin

## Common Commands

### Run management commands:

```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Create a superuser
docker-compose exec web python manage.py createsuperuser

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# Access Django shell
docker-compose exec web python manage.py shell

# Run any Django management command
docker-compose exec web python manage.py <command>
```

### Database operations:

```bash
# Access PostgreSQL shell
docker-compose exec db psql -U postgres -d bluepages

# Create database backup
docker-compose exec db pg_dump -U postgres bluepages > backup.sql

# Restore database
docker-compose exec -T db psql -U postgres bluepages < backup.sql

# Or restore from a dump file
cat backup.sql | docker-compose exec -T db psql -U postgres bluepages
```

### View logs:

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f db
```

### Stop containers:

```bash
# Stop containers (keeps data)
docker-compose stop

# Stop and remove containers (keeps volumes/data)
docker-compose down

# Stop and remove containers + volumes (deletes database!)
docker-compose down -v
```

## Development Workflow

### Hot Reloading

The `web` service mounts your local code directory, so changes to Python files are reflected immediately thanks to Django's development server auto-reload.

### Install New Python Packages

1. Add package to `requirements.txt`
2. Rebuild the container:

```bash
docker-compose up --build web
```

### Access Container Shell

```bash
# Python/Django container
docker-compose exec web bash

# Database container
docker-compose exec db bash
```

### Running Tests

```bash
docker-compose exec web python manage.py test
```

## Troubleshooting

### Container won't start

```bash
# Check logs
docker-compose logs web
docker-compose logs db

# Rebuild from scratch
docker-compose down -v
docker-compose up --build
```

### Database connection issues

```bash
# Check if database is ready
docker-compose exec db pg_isready -U postgres

# Check environment variables
docker-compose exec web env | grep DB_

# Verify database exists
docker-compose exec db psql -U postgres -l
```

### Permission issues with volumes

```bash
# Fix permissions on mounted volumes
sudo chown -R $USER:$USER bluepages/static_root bluepages/media_root
```

### Reset everything

```bash
# Remove all containers, volumes, and start fresh
docker-compose down -v
docker-compose up --build
```

## Production Deployment

For production, create a `docker-compose.prod.yml`:

```yaml
version: "3.8"

services:
  db:
    image: postgis/postgis:16-3.4
    restart: always
    environment:
      POSTGRES_DB: bluepages
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${DB_PASSWORD} # Use .env file
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - internal

  web:
    build: .
    restart: always
    command: gunicorn bluepages.wsgi:application --bind 0.0.0.0:8000 --workers 4
    volumes:
      - static_volume:/app/bluepages/static_root
      - media_volume:/app/bluepages/media_root
    environment:
      - DOCKER_CONTAINER=1
      - DEBUG=False
      - DB_NAME=bluepages
      - DB_USER=postgres
      - DB_PASSWORD=${DB_PASSWORD}
      - DB_HOST=db
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - db
    networks:
      - internal
      - web

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - static_volume:/app/static:ro
      - media_volume:/app/media:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - web
    networks:
      - web

networks:
  internal:
  web:

volumes:
  postgres_data:
  static_volume:
  media_volume:
```

Run with: `docker-compose -f docker-compose.prod.yml up -d`

## Notes

- PostgreSQL 16 with PostGIS 3.4 (matches Ubuntu 24.04)
- Python 3.11 (compatible with Django 3.2+)
- Development server runs on port 8000
- Database runs on port 5432 (exposed for local tools)
- Code changes are live-reloaded in development
- Data persists in Docker volumes even when containers are stopped
