#!/usr/bin/env bash
set -o errexit

# Explicitly upgrade pip and set Python path
python -m pip install --upgrade pip

# Install exact versions with pip (no cache)
pip install --no-cache-dir -r requirements.txt

# Verify gunicorn is installed
pip show gunicorn || echo "Gunicorn not found!"

# Database setup
python manage.py migrate

# Static files
python manage.py collectstatic --noinput