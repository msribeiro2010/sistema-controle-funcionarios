#!/usr/bin/env bash
set -o errexit

# Apenas o essencial
pip install -r requirements.txt
mkdir -p staticfiles
python manage.py migrate --noinput 