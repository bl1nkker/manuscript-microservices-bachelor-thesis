# Manuscript App Micrservices

## How to get started locally

### 1. Run docker-compose with postgres and redis:

`deployment/local/up.sh`

### 3. Run microservices:

#### a. Install dependencies inside each microservice (Pipenv required):

`pipenv install -r requirements.txt`

#### b. Run migrations:

`python manage.py migrate`

#### c. Run microservices:

- event:
  `gunicorn ms_event.wsgi:application -c gunicorn.conf.py`
- teams:
  `gunicorn ms_teams.wsgi:application -c gunicorn.conf.py`
- users:
  `gunicorn ms_users.wsgi:application -c gunicorn.conf.py`

## Extras:

PORTS:

- 16010 - events
- 16020 - teams
- 16030 - users

TODO:

- set views for teams
- write documentation for events
- refactor message broker

- think about notification service

- logger
- add message broker tests
- check message broker
