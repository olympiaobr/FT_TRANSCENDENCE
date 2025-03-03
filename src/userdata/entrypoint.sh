#!/bin/sh

echo "Waiting for PostgreSQL..."
while ! nc -z $USERDATA_DB_NAME $USERDATA_DB_PORT; do
    sleep 0.2
done
echo "PostgreSQL started"

echo "Running migrations..."
python manage.py makemigrations
python manage.py migrate

exec "$@"