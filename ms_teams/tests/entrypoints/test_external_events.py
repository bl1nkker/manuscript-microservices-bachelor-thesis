from django.test import TestCase
from unittest.mock import MagicMock, call
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
        mb.channel.queue_declare.assert_has_calls([
            call(queue=settings.RABBITMQ_QUEUE_USER_CREATED, durable=True),
            call(queue=settings.RABBITMQ_QUEUE_EVENT_CREATE, durable=True),
            call(queue=settings.RABBITMQ_QUEUE_EVENT_EDIT, durable=True),
        ])
        mb.queue_bind.assert_has_calls([
            call(queue=settings.RABBITMQ_QUEUE_USER_CREATED,
                 routing_key=settings.RABBITMQ_USER_CREATE_ROUTING_KEY),
            call(queue=settings.RABBITMQ_QUEUE_EVENT_CREATE,
                 routing_key=settings.RABBITMQ_EVENT_CREATE_ROUTING_KEY),
            call(queue=settings.RABBITMQ_QUEUE_EVENT_EDIT,
                 routing_key=settings.RABBITMQ_EVENT_EDIT_ROUTING_KEY),
        ])
        mb.channel.basic_consume.assert_has_calls([
            # queue=queue, on_message_callback=callback, auto_ack=True)
            call(queue=settings.RABBITMQ_QUEUE_USER_CREATED,
                 on_message_callback=event_consumer.handle_user_creation, auto_ack=True),
            call(queue=settings.RABBITMQ_QUEUE_EVENT_CREATE,
                 on_message_callback=event_consumer.handle_event_creation, auto_ack=True),
            call(queue=settings.RABBITMQ_QUEUE_EVENT_EDIT,
                 on_message_callback=event_consumer.handle_event_edit, auto_ack=True),
        ])
        mb.start_consuming.assert_called_once()

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

    def test_handle_event_creation_event_should_create_event(self):
        # Mock the parameters for RabbitMQ channel, method, properties, and body
        ch = MagicMock()
        method = MagicMock()
        properties = MagicMock()
        body = '{"id": 999, "name": "Test Event", "is_active": false}'

        # Call the handle_event_creation function with the mocked parameters
        event_consumer.handle_event_creation(ch, method, properties, body)

        # Assert that the Event object was created correctly
        self.assertTrue(models.Event.objects.filter(id=999).exists())
        self.assertFalse(models.Event.objects.filter(id=999).first().is_active)
        self.assertEqual(models.Event.objects.filter(
            id=999).first().name, 'Test Event')

    def test_handle_event_edit_event_should_edit_event(self):
        # Create an Event object
        models.Event.objects.create(id=999, name='Test Event', is_active=False)

        # Mock the parameters for RabbitMQ channel, method, properties, and body
        ch = MagicMock()
        method = MagicMock()
        properties = MagicMock()
        body = '{"id": 999, "name": "Test Event Edited", "is_active": true}'

        # Call the handle_event_edit function with the mocked parameters
        event_consumer.handle_event_edit(ch, method, properties, body)

        # Assert that the Event object was edited correctly
        self.assertTrue(models.Event.objects.filter(id=999).exists())
        self.assertTrue(models.Event.objects.filter(id=999).first().is_active)
        self.assertEqual(models.Event.objects.filter(
            id=999).first().name, 'Test Event Edited')
