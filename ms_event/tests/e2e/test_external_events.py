import pika
import json

from django.test import TestCase
from django.conf import settings
import app.models as models


import service_layer.message_broker as mb
import entrypoints.event_consumer as ec


class TestUserEvents():

    def setUp(self) -> None:
        credentials = pika.URLParameters(settings.RABBITMQ_CONNECTION_URL)
        self.mb = mb.RabbitMQ(
            credentials.host, credentials.port, credentials.credentials.username, credentials.credentials.password, exchange=settings.RABBITMQ_EXCHANGE_NAME)
        self.mb.connect()

    def test_on_user_create_route_should_create_user(self):
        self.assertEqual(models.User.objects.count(), 0)
        # Subscribe to event
        # Send message
        with self.mb as mb:
            user_data = {
                'id': 69,
                'username': 'test@gmail.com',
                'email': 'test@gmail.com',
                'first_name': 'Test',
                'last_name': 'User',
            }
            # Subscribe to the queue and start consuming messages
            mb.subscribe(
                queue=settings.RABBITMQ_EVENT_QUEUE, callback=ec.handle_user_creation, routing_key=settings.RABBITMQ_EVENT_ROUTING_KEY)
            # Publish a message to an exchange
            mb.publish(
                routing_key=settings.RABBITMQ_USER_CREATE_ROUTING_KEY, message=json.dumps(user_data))
        self.assertEqual(models.User.objects.count(), 1)
        self.assertEqual(models.ManuscriptUser.objects.count(), 1)
        self.assertEqual(models.ManuscriptUser.objects.first().id, 69)
        self.assertEqual(models.ManuscriptUser.objects.first().user.username,
                         user_data['username'])
        self.assertEqual(models.ManuscriptUser.objects.first().user.email,
                         user_data['email'])
        self.assertEqual(models.ManuscriptUser.objects.first().user.first_name,
                         user_data['first_name'])
        self.assertEqual(models.ManuscriptUser.objects.first().user.last_name,
                         user_data['last_name'])
