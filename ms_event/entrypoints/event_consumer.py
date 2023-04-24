import service_layer.message_broker as mb
from django.conf import settings
import pika
import json
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'ms_event.settings'


def start(message_broker):
    print('Starting event consumer...')

    with message_broker:
        message_broker.subscribe(
            queue=settings.RABBITMQ_QUEUE, callback=handle_user_creation, routing_key=settings.RABBITMQ_USER_CREATE_ROUTING_KEY)
        message_broker.start_consuming()


def handle_user_creation(ch, method, properties, body):
    import django
    django.setup()
    import app.models as models

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


if __name__ == '__main__':
    message_broker = mb.RabbitMQ()
    start(message_broker=message_broker)
