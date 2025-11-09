#!/bin/bash

# Start Redis
echo "Starting Redis..."
redis-server &

# Wait until Redis is ready
until redis-cli ping | grep -q PONG; do
  echo "Waiting for Redis..."
  sleep 1
done

# Start Celery Worker
echo "Starting Celery Worker..."
celery -A Nexo worker -l info &

# Optionally start Celery Beat
# echo "Starting Celery Beat..."
# celery -A Nexo beat -l info &

# Start Django server
echo "Starting Django Server..."
python manage.py runserver
