release: python manage.py migrate
web: gunicorn accumate_backend.wsgi --log-file -
worker: celery -A accumate_backend.celeryapp:app worker --loglevel=info