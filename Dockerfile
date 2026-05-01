# Stage 1: Build JS assets (one per package.json)
FROM node:20-slim AS js-app-builder

WORKDIR /js/app
COPY bluepages/app/static/app/js/app/package*.json ./
RUN npm i
COPY bluepages/app/static/app/js/app/ ./
RUN mkdir -p /js/dist && npm run build

FROM node:20-slim AS record-suggestion-builder

WORKDIR /js/record_suggestion
COPY bluepages/app/static/app/js/record_suggestion/package*.json ./
RUN npm i
COPY bluepages/app/static/app/js/record_suggestion/ ./
RUN npx webpack --mode=development

FROM node:20-slim AS region-picker-builder

WORKDIR /js/region_picker
COPY bluepages/app/static/app/js/region_picker/package*.json ./
RUN npm ci
COPY bluepages/app/static/app/js/region_picker/ ./
RUN npx webpack --mode=development

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
COPY --from=js-app-builder /js/dist/ /app/bluepages/app/static/app/js/dist/
COPY --from=record-suggestion-builder /js/record_suggestion/dist/ /app/bluepages/app/static/app/js/dist/
COPY --from=region-picker-builder /js/region_picker/dist/ /app/bluepages/app/static/app/js/dist/
RUN mkdir -p /opt/bluepages-js-dist && \
    cp -a /app/bluepages/app/static/app/js/dist/. /opt/bluepages-js-dist/

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