# Manuscript App Microservices

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

- docker orchestration tool
- nocodb
- jenkins
- rabbitmq clasterization
- get participation requests list
- filters

! dashboards
! k8s

if there are any processes:

- lsof -i tcp:16010
- sudo kill <process_id>


### Executables:
`up:
	docker-compose up --build

down:
	docker-compose down -v

rq:
	brew services start rabbitmq

build:
	cd ms_event && docker build -t ms_event . && docker tag ms_event blinkker/ms_event:latest && docker push blinkker/ms_event:latest
	cd ms_teams && docker build -t ms_teams . && docker tag ms_teams blinkker/ms_teams:latest && docker push blinkker/ms_teams:latest
	cd ms_users && docker build -t ms_users . && docker tag ms_users blinkker/ms_users:latest && docker push blinkker/ms_users:latest
	cd ms_notifications && docker build -t ms_notifications . && docker tag ms_notifications blinkker/ms_notifications:latest && docker push blinkker/ms_notifications:latest
	cd ms_telegram && docker build -t ms_telegram . && docker tag ms_telegram blinkker/ms_telegram:latest && docker push blinkker/ms_telegram:latest
	cd proxy && docker build -t proxy . && docker tag proxy blinkker/proxy:latest && docker push blinkker/proxy:latest`
	
