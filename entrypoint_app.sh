#!/bin/bash
set -e

until pg_isready -h $DB_HOST -p $DB_PORT; do
  echo "Waiting for database..."
  sleep 1
done
echo "Database is ready!"

if redis-cli -h $REDIS_HOST -p $REDIS_PORT ping | grep -q "PONG"; then
    echo "Redis is ready to accept connections."
else
    echo "Redis is not ready or unreachable."
fi

python manage.py makemigrations
python manage.py migrate 
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
#exec tail -f /dev/null
#exec python manage.py runserver 0.0.0.0:8000
