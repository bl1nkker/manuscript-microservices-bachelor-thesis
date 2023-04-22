import pika
import json
import service_layer.message_broker as mb
from django.conf import settings
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'ms_event.settings'


def start():
    print('Starting event consumer...')
    credentials = pika.URLParameters(settings.RABBITMQ_CONNECTION_URL)
    message_broker = mb.RabbitMQ(
        credentials.host, credentials.port, credentials.credentials.username, credentials.credentials.password, exchange=settings.RABBITMQ_EXCHANGE_NAME)
    message_broker.connect()

    message_broker.subscribe(
        queue=settings.RABBITMQ_QUEUE, callback=handle_user_creation, routing_key=settings.RABBITMQ_USER_CREATE_ROUTING_KEY)


def handle_user_creation(ch, method, properties, body):
    data = json.loads(body)
    import django
    django.setup()
    import app.models as models
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
    start()
