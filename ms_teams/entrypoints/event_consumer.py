import pika
import json
import service_layer.message_broker as mb
from django.conf import settings
import os
import core.logger as logger
os.environ['DJANGO_SETTINGS_MODULE'] = 'ms_teams.settings'


def start(message_broker):
    logger.info(user='CONSUMER',
                message='Starting message broker connection...', logger=logger.mb_logger)
    try:
        message_broker.subscribe(
            queue=settings.RABBITMQ_QUEUE, callback=handle_user_creation, routing_key=settings.RABBITMQ_USER_CREATE_ROUTING_KEY)
        message_broker.subscribe(
            queue=settings.RABBITMQ_QUEUE, callback=handle_event_creation, routing_key=settings.RABBITMQ_EVENT_CREATE_ROUTING_KEY)
        message_broker.subscribe(
            queue=settings.RABBITMQ_QUEUE, callback=handle_event_edit, routing_key=settings.RABBITMQ_EVENT_EDIT_ROUTING_KEY)
        message_broker.start_consuming()
    except Exception as e:
        logger.error(user='CONSUMER',
                     message=f'Error while consuming message: {e}', logger=logger.mb_logger)
    finally:
        logger.info(user='CONSUMER',
                    message='Closing message broker connection...', logger=logger.mb_logger)


def handle_user_creation(ch, method, properties, body):
    data = json.loads(body)
    import django
    django.setup()
    import app.models as models
    user = models.User.objects.create(
        username=data['username'],
        email=data['username'],
        first_name=data['first_name'],
        last_name=data['last_name'],
    )
    models.ManuscriptUser.objects.create(
        id=data['id'],
        user=user
    )


def handle_event_creation(ch, method, properties, body):
    data = json.loads(body)
    import django
    django.setup()
    import app.models as models
    models.Event.objects.create(
        name=data['name'],
        id=data['id'],
        is_active=data['is_active'],
    )


def handle_event_edit(ch, method, properties, body):
    data = json.loads(body)
    import django
    django.setup()
    import app.models as models
    event = models.Event.objects.get(id=data['id'])
    event.name = data['name']
    event.is_active = data['is_active']
    event.save()


if __name__ == '__main__':
    message_broker = mb.RabbitMQ()
    start(message_broker=message_broker)
