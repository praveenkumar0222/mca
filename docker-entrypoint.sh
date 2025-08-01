#!/bin/bash
echo "Collecting static files..."
python manage.py collectstatic --no-input

# Start Gunicorn
echo "Starting Gunicorn..."
exec gunicorn -w 4 -b 0.0.0.0:8000 backend.wsgi:application
