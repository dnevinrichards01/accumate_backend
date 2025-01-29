#!/bin/bash
set -e

pip install -e /code/build_files/accumate_robinstocks

until pg_isready -h $DB_HOST -p $DB_PORT; do
  echo "Waiting for database..."
  sleep 1
done
echo "Database is ready!"

show_migrations=$(eval "python manage.py showmigrations")
if echo [$show_migrations | grep -q "[ ]"]; then
    echo "making migrations"
    python manage.py makemigrations --noinput
    python manage.py migrate --noinput
else
    echo "migrations already made"
fi

exec tail -f /dev/null
