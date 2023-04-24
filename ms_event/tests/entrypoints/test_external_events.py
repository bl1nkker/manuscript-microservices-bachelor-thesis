from django.test import TestCase
from unittest.mock import MagicMock
from django.conf import settings

import entrypoints.event_consumer as event_consumer
import app.models as models


class TestExternalEvents(TestCase):
    def setUp(self):
        pass

    def test_event_consumer_subscribes_to_correct_routing_keys(self):
        # Mock the RabbitMQ class
        mb = MagicMock()

        # Call the start function
        event_consumer.start(mb)

        # Assert that the subscribe function was called with the correct parameters
        mb.subscribe.assert_called_with(
            queue=settings.RABBITMQ_QUEUE, callback=event_consumer.handle_user_creation, routing_key=settings.RABBITMQ_USER_CREATE_ROUTING_KEY)

    def test_handle_user_creation_event_should_create_user(self):
        # Mock the parameters for RabbitMQ channel, method, properties, and body
        ch = MagicMock()
        method = MagicMock()
        properties = MagicMock()
        body = '{"id": 999, "username": "testuser", "email": "test@example.com", "first_name": "Test", "last_name": "User"}'

        # Call the handle_user_creation function with the mocked parameters
        event_consumer.handle_user_creation(ch, method, properties, body)

        # Assert that the User and ManuscriptUser objects were created correctly
        self.assertTrue(models.User.objects.filter(
            username='testuser').exists())
        self.assertTrue(models.ManuscriptUser.objects.filter(id=999).exists())
