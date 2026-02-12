"""
Docker-specific settings that override base settings.py
This file is imported at the end of settings.py when running in Docker.
"""
import os

# Database configuration from environment variables
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.environ.get('DB_NAME', 'bluepages'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'postgres'),
        'HOST': os.environ.get('DB_HOST', 'db'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Debug mode from environment
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# Allow all hosts in Docker (configure properly for production)
ALLOWED_HOSTS = ['*']

# Static and media files
STATIC_ROOT = '/app/bluepages/static_root'
MEDIA_ROOT = '/app/bluepages/media_root'
MEDIA_URL = '/media/'
