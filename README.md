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
- 16040 - notifications

TODO:

- rewrite tests
- github actions
- telegram bot

- something wrong with notification proxy
- filters
- add user participation status to response with team
- add notification status
- add user update description, phone
- send notification interface

- add images to response
- dashboards
- k8s

if there are any processes:

- lsof -i tcp:16010
- sudo kill <process_id>
