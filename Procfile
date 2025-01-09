release: python manage.py migrate
web: python manage.py collectstatic --no-input && gunicorn core.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --threads 2 --timeout 60
