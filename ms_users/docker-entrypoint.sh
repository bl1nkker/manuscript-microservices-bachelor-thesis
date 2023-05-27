#!/bin/bash
# Check the value of the SERVICE_TYPE environment variable
if [ "$SERVICE_TYPE" = "service" ]; then
  # Run the gunicorn command
  ./wait-for-it.sh ms_users_db:5432 -- 
  python3 manage.py makemigrations
  python3 manage.py migrate
  exec gunicorn ms_users.wsgi:application -c gunicorn.conf.py
elif [ "$SERVICE_TYPE" = "consumer" ]; then
  # Run the event consumer command
  ./wait-for-it.sh ms_users:16010 --
  ./wait-for-it.sh rabbitmq:5672 -- python3 -m entrypoints.event_consumer
fi
