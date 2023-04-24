import pika
import json
from django.conf import settings
from django.test import TestCase, Client


import service_layer.message_broker as mb
import app.models as models


class TestUserEvents():
    def setUp(self) -> None:
        self.client = Client()
        credentials = pika.URLParameters(settings.RABBITMQ_CONNECTION_URL)
        self.mb = mb.RabbitMQ(
            credentials.host, credentials.port, credentials.credentials.username, credentials.credentials.password, exchange=settings.RABBITMQ_EXCHANGE_NAME)
        self.mb.connect()

    def test_user_register_should_emit_user_created_event(self):
        def callback(ch, method, properties, body):
            user = models.ManuscriptUser.objects.last()
            self.assertEqual(body, json.dumps(user.to_dict()))
            ch.stop_consuming()
        self.assertEqual(models.User.objects.count(), 0)

        body = {
            "email": "test_mb@gmail.com",
            "first_name": "Test",
            "last_name": "User",
            "password": "test1234",
        }
        response = self.client.post(
            "/register/", body, content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(models.User.objects.count(), 1)

        # Subscribe to the queue and start consuming messages
        self.mb.subscribe(
            queue=settings.RABBITMQ_QUEUE, callback=callback, routing_key=settings.RABBITMQ_USER_CREATE_ROUTING_KEY)
