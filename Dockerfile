# Stage 1: Build JS assets 
FROM node:20-slim AS js-builder

WORKDIR /frontend
COPY frontend/package.json .
# Copy each submodule's package.json first for better layer caching
COPY frontend/app/package.json ./app/
COPY frontend/region_picker/package.json ./region_picker/
COPY frontend/record_suggestion/package.json ./record_suggestion/
COPY frontend/admin/package.json ./admin/

RUN npm run install

# Now copy all source files and build
COPY frontend/ .
RUN npm run build

# Stage 2: Build Python/Django image
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

# Copy only the compiled dist output from the JS builder
# Store in a separate location so entrypoint.sh can sync it after the project COPY
COPY --from=js-builder /frontend/dist/ /opt/bluepages-js-dist/

# Copy the rest of the project (no node_modules, no JS source)
COPY . /app/

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