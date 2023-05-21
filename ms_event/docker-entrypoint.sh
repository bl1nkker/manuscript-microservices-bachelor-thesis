#!/bin/bash
./wait-for-it.sh ms_event_db:5432 -- python manage.py migrate
exec gunicorn ms_event.wsgi:application -c gunicorn.conf.py
