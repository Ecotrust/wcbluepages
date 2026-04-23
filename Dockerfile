# Stage 1: Build JS assets
FROM node:20-slim AS js-builder

WORKDIR /js
COPY bluepages/app/static/app/js/app/package*.json ./
RUN npm ci
COPY bluepages/app/static/app/js/app/ ./
RUN mkdir -p /dist && npm run build

# Stage 2: Python application
# Use Python 3.11 slim image as base
FROM python:3.11-slim-bookworm

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    libpq-dev \
    postgresql-client \
    gdal-bin \
    libgdal-dev \
    libproj-dev \
    proj-bin \
    binutils \
    libspatialindex-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy project files
COPY . /app/

# Copy compiled JS assets from js-builder stage
COPY --from=js-builder /dist/ /app/bluepages/app/static/app/js/dist/

# Make entrypoint script executable
RUN chmod +x /app/entrypoint.sh

# Create necessary directories
RUN mkdir -p /app/bluepages/static_root /app/bluepages/media_root

# Set working directory to Django project
WORKDIR /app/bluepages

# Expose port
EXPOSE 8000

# Use entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]