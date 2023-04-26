

import pika
from abc import ABC, abstractmethod
import os
from django.conf import settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'ms_teams.settings'


class AbstractMessageBroker(ABC):
    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def publish(self, exchange, routing_key, message):
        pass

    @abstractmethod
    def subscribe(self, exchange, queue, callback, routing_key):
        pass

    @abstractmethod
    def disconnect(self):
        pass


class RabbitMQ(AbstractMessageBroker):

    def __init__(self, host: str = settings.RABBITMQ_HOST, port: str = settings.RABBITMQ_PORT, username: str = settings.RABBITMQ_USER,
                 password: str = settings.RABBITMQ_PASSWORD, exchange: str = settings.RABBITMQ_EXCHANGE_NAME, vhost=settings.RABBITMQ_VHOST, exchange_type='topic'):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.exchange = exchange

        self.vhost = vhost

        self.connection = None
        self.channel = None

        self.exchange_type = exchange_type

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def connect(self):
        credentials = pika.credentials.PlainCredentials(
            self.username, self.password)
        parameters = pika.ConnectionParameters(
            host=self.host, port=self.port, credentials=credentials, virtual_host=self.vhost)
        if self.vhost == 'test':
            parameters = pika.ConnectionParameters(
                host=self.host, port=self.port, credentials=credentials)
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()
        self.channel.exchange_declare(
            exchange=self.exchange, exchange_type=self.exchange_type, durable=True)

    def publish(self, routing_key, message):
        self.channel.basic_publish(
            exchange=self.exchange, routing_key=routing_key, body=message, properties=pika.BasicProperties(delivery_mode=2))

    def subscribe(self, queue, callback, routing_key):
        result = self.channel.queue_declare(queue=queue, durable=True)
        queue_name = result.method.queue
        self.channel.queue_bind(
            exchange=self.exchange, queue=queue_name, routing_key=routing_key)
        self.channel.basic_consume(
            queue=queue_name, on_message_callback=callback, auto_ack=True)

    def start_consuming(self):
        self.channel.start_consuming()

    def disconnect(self):
        self.channel.close()
        self.connection.close()

    def consume_last_message(self, queue):
        method, properties, body = self.channel.basic_get(
            queue=queue, auto_ack=True)
        return body
