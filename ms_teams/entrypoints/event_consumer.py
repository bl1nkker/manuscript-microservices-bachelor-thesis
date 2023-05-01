import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'ms_teams.settings'
import json
import service_layer.message_broker as mb
import django
django.setup()
import app.models as models
from django.conf import settings
import core.logger as logger


def start(message_broker: mb.RabbitMQ):
    logger.info(user='CONSUMER',
                message='Starting message broker connection...', logger=logger.mb_logger)
    try:
        binds = [
            (settings.RABBITMQ_QUEUE_USER_CREATED, settings.RABBITMQ_USER_CREATE_ROUTING_KEY, handle_user_creation),
            (settings.RABBITMQ_QUEUE_EVENT_CREATE, settings.RABBITMQ_EVENT_CREATE_ROUTING_KEY, handle_event_creation),
            (settings.RABBITMQ_QUEUE_EVENT_EDIT, settings.RABBITMQ_EVENT_EDIT_ROUTING_KEY, handle_event_edit),
        ]
        with message_broker:
            for item in binds:
                (queue, routing_key, callback) = item
                message_broker.channel.queue_declare(queue=queue, durable=True)
                message_broker.queue_bind(queue=queue, routing_key=routing_key)
                message_broker.channel.basic_consume(
                    queue=queue, on_message_callback=callback, auto_ack=True)
            message_broker.start_consuming()
    except Exception as e:
        logger.error(user='CONSUMER',
                     message=f'Error while consuming message: {e}', logger=logger.mb_logger)
    finally:
        logger.info(user='CONSUMER',
                    message='Closing message broker connection...', logger=logger.mb_logger)

def handle_user_creation(ch, method, properties, body):
    logger.info(user='CONSUMER',
                message=f'Handle user creation with body: {body}', logger=logger.mb_logger)
    data = json.loads(body)
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
    logger.info(user='CONSUMER',
                message=f'User created: {user}', logger=logger.mb_logger)


def handle_event_creation(ch, method, properties, body):
    logger.info(user='CONSUMER',
                message=f'Handle event creation with body: {body}', logger=logger.mb_logger)
    try:
        data = json.loads(body)
        models.Event.objects.create(
            name=data['name'],
            id=data['id'],
            is_active=data['is_active'],
        )
        logger.info(user='CONSUMER',
                    message=f'Event created: {data}', logger=logger.mb_logger)
    except Exception as e:
        logger.error(user='CONSUMER',
                     message=f'Error while handling event creation: {e}', logger=logger.mb_logger)


def handle_event_edit(ch, method, properties, body):
    logger.info(user='CONSUMER',
                message=f'Handle event edit with body: {body}', logger=logger.mb_logger)
    try:
        data = json.loads(body)
        event = models.Event.objects.get(id=data['id'])
        event.name = data['name']
        event.is_active = data['is_active']
        event.save()
        logger.info(user='CONSUMER',
                    message=f'Event edited: {data}', logger=logger.mb_logger)
    except Exception as e:
        logger.error(user='CONSUMER',
                     message=f'Error while handling event edit: {e}', logger=logger.mb_logger)


if __name__ == '__main__':
    message_broker = mb.RabbitMQ()
    start(message_broker=message_broker)
