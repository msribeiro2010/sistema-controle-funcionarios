#!/bin/bash
export PATH="/opt/render/project/src/.venv/bin:$PATH"
export PYTHONPATH="/opt/render/project/src:$PYTHONPATH"
cd /opt/render/project/src
exec /opt/render/project/src/.venv/bin/gunicorn core.wsgi:application --bind=0.0.0.0:$PORT --workers=4 --timeout=120 --log-level=debug 