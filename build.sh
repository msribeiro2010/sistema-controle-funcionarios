#!/usr/bin/env bash
set -o errexit

echo "Installing dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "Running migrations..."
python manage.py migrate --noinput

echo "Build completed successfully!" 