#!/bin/bash
set -e

# This script runs automatically when the PostgreSQL container is first initialized
# It will only run if the database is empty (first time setup)

echo "Importing database dump..."

# Import the SQL dump, ignoring meta-command errors
psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v ON_ERROR_STOP=0 < /tmp/db_dump.sql

echo "Database import completed!"
