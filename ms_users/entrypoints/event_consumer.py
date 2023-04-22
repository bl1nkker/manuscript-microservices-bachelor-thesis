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

    # Subscribe for different events


if __name__ == '__main__':
    start()
