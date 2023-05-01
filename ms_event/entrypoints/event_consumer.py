import json
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'ms_event.settings'
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
    try:
        data = json.loads(body)
        user = models.User.objects.create(
            username=data['username'],
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
        )
        models.ManuscriptUser.objects.create(
            id=data['id'],
            user=user
        )
        logger.info(user='CONSUMER',
                    message=f'User created: {user}', logger=logger.mb_logger)
    except Exception as e:
        logger.error(user='CONSUMER',
                     message=f'Error while user creation: {e}', logger=logger.mb_logger)


if __name__ == '__main__':
    message_broker = mb.RabbitMQ()
    start(message_broker=message_broker)
