import pika
import json
import service_layer.message_broker as mb
from django.conf import settings
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'ms_event.settings'


def start():
    credentials = pika.URLParameters(settings.RABBITMQ_CONNECTION_URL)
    message_broker = mb.RabbitMQ(
        credentials.host, credentials.port, credentials.credentials.username, credentials.credentials.password, exchange=settings.RABBITMQ_EXCHANGE_NAME)
    message_broker.connect()

    message_broker.publish(
        routing_key=settings.RABBITMQ_USER_CREATE_ROUTING_KEY, message=json.dumps({
            'id': 69,
            'username': 'test@gmail.com',
            'email': 'test@gmail.com',
            'first_name': 'Test',
            'last_name': 'User',
        }))


if __name__ == '__main__':
    start()
