#!/bin/bash
source .venv/bin/activate
exec python -m gunicorn core.wsgi:application --bind=0.0.0.0:$PORT --workers=4 --timeout=120 