web: gunicorn core.wsgi:application --bind 0.0.0.0:$PORT --workers 4
release: python manage.py migrate
