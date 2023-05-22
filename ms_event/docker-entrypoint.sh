#!/bin/bash
# Check the value of the SERVICE_TYPE environment variable
if [ "$SERVICE_TYPE" = "service" ]; then
  # Run the gunicorn command
  ./wait-for-it.sh ms_event_db:5432 -- 
  python manage.py makemigrations
  python manage.py migrate
  exec gunicorn ms_event.wsgi:application -c gunicorn.conf.py
elif [ "$SERVICE_TYPE" = "consumer" ]; then
  # Run the event consumer command
  ./wait-for-it.sh ms_event:16010 --
  ./wait-for-it.sh rabbitmq:5672 -- python -m entrypoints.event_consumer
fi
