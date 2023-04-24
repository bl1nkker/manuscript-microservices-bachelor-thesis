import json

from django.test import TestCase
from django.conf import settings
import app.models as models


import service_layer.message_broker as mb
import entrypoints.event_consumer as ec


class TestRabbitMQ(TestCase):

    def setUp(self) -> None:
        self.mb = mb.RabbitMQ(exchange=settings.RABBITMQ_TEST_EXCHANGE_NAME)

    def test_publish_message_should_publish_message(self):
        q = 'test_publish_message_should_publish_message.queue'
        with self.mb as mb:
            message = 'Hello World'
            mb.channel.queue_declare(
                queue=q, durable=True, exclusive=True)
            mb.channel.queue_bind(exchange=settings.RABBITMQ_TEST_EXCHANGE_NAME,
                                  queue=q, routing_key='test.data.rk')
            # Publish a message to an exchange
            mb.publish(
                routing_key='test.data.rk', message=json.dumps(message))

            method, properties, body = mb.channel.basic_get(
                queue=q, auto_ack=True)

            self.assertEqual(json.loads(body), message)

    def test_subscribe_should_return_message(self):
        with self.mb as mb:
            message = 'Hello World'

            def callback(ch, method, properties, body):
                self.assertEqual(json.loads(body), message)
                ch.stop_consuming()

            mb.publish(routing_key='test.data.rk', message=json.dumps(message))
            mb.subscribe(queue='test_subscribe_should_return_message', callback=callback,
                         routing_key='test.data.rk')

    def test_subscribe_and_consume_message_should_get_messages_from_single_queue(self):
        q = 'test_subscribe_and_consume_message_should_get_messages_from_single_queue.q'
        with self.mb as mb:
            message_for_sub = 'Hello Sub'
            message_for_con = 'Hello Consume'

            def callback(ch, method, properties, body):
                self.assertEqual(json.loads(body), message_for_sub)
                ch.stop_consuming()

            mb.publish(routing_key='test.data.rk',
                       message=json.dumps(message_for_con))
            mb.publish(routing_key='test.data.rk',
                       message=json.dumps(message_for_sub))
            mb.subscribe(queue=q, callback=callback,
                         routing_key='test.data.rk')
