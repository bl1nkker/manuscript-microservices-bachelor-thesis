import pika

from django.test import TestCase
from django.conf import settings


import service_layer.message_broker as mb


class RabbitMQMessageBrokerTestCase():
    def setUp(self):
        credentials = pika.URLParameters(settings.RABBITMQ_CONNECTION_URL)
        self.rabbitmq = mb.RabbitMQ(
            credentials.host, credentials.port, credentials.credentials.username, credentials.credentials.password, exchange=settings.RABBITMQ_EXCHANGE_NAME)
        self.rabbitmq.connect()

    def test_connect(self):
        with self.rabbitmq as rabbitmq:
            self.assertIsInstance(
                rabbitmq.connection, pika.adapters.blocking_connection.BlockingConnection)
            self.assertIsInstance(rabbitmq.channel,
                                  pika.adapters.blocking_connection.BlockingChannel)

    def test_RABBITMQ_QUEUE_receive_message(self):
        # Define a callback function for handling received messages
        def callback(ch, method, properties, body):
            self.assertEqual(body, b"Hello, RabbitMQ!")
            ch.stop_consuming()

        with self.rabbitmq as rabbitmq:
            # Publish a message to an exchange
            rabbitmq.publish(
                routing_key=settings.RABBITMQ_EVENT_ROUTING_KEY, message="Hello, RabbitMQ!")

            # Subscribe to the queue and start consuming messages
            rabbitmq.subscribe(
                queue=settings.RABBITMQ_QUEUE, callback=callback, routing_key=settings.RABBITMQ_EVENT_ROUTING_KEY)

            # Wait for the callback to be invoked
            rabbitmq.channel.start_consuming()

    def test_disconnect_after_usage(self):
        with self.rabbitmq:
            pass
        self.assertIsNone(self.rabbitmq.connection)
        self.assertIsNone(self.rabbitmq.channel)
