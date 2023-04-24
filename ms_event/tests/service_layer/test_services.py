import json

from django.test import TestCase, override_settings
from django.conf import settings

from unittest.mock import patch, Mock
from service_layer.result import Result
import service_layer.services as services
import service_layer.unit_of_work as uow
import service_layer.message_broker as mb
import core.exceptions as exceptions


@override_settings(DEBUG=True)
class TestEventServices(TestCase):

    def setUp(self) -> None:
        self.uow = uow.FakeUnitOfWork()
        self.user = self.uow.user.create(username="test", password="test")
        return super().setUp()

    # Get event

    def test_get_event_service_should_return_result_with_event_by_id(self):
        event = self.uow.event.create(**{
            "name": "test_event",
            "image": 'test_image',
            "location": 'Almaty',
            "location_url": 'https://www.google.com',
            "description": 'Test description',
            "full_description": 'Test full description',
            "start_date": '2020-01-01',
            "end_date": '2020-01-02',
            "author": self.user,
            "tags": ['test_tag1', 'test_tag2'],
        })
        expected = Result(data=event.to_dict(), error=None)
        result = services.get_event_service(uow=self.uow, id=event.id)
        self.assertEqual(result, expected)

    def test_get_event_service_should_return_result_with_error_when_event_is_not_found(self):
        expected = Result(data=None, error=exceptions.EventNotFoundException)
        result = services.get_event_service(uow=self.uow, id=999)
        self.assertEqual(result, expected)

    # Get list of events

    def test_list_events_service_should_return_list_of_events_by_location(self):
        for i in range(3):
            event = self.uow.event.create(**{
                "name": "test_event",
                "image": 'test_image',
                "location": 'Almaty',
                "location_url": 'https://www.google.com',
                "description": 'Test description',
                "full_description": 'Test full description',
                "start_date": '2020-01-01',
                "end_date": '2020-01-02',
                "author": self.user,
                "tags": ['test_tag1', 'test_tag2'],
            })
        for i in range(3):
            event = self.uow.event.create(**{
                "name": "test_event",
                "image": 'test_image',
                "location": 'Qostanay',
                "location_url": 'https://www.google.com',
                "description": 'Test description',
                "full_description": 'Test full description',
                "start_date": '2020-01-01',
                "end_date": '2020-01-02',
                "author": self.user,
                "tags": ['test_tag1', 'test_tag2'],
            })
        expected = Result(data=[
            event.to_dict() for event in self.uow.event.list(location='Almaty')
        ], error=None)
        result = services.list_events_service(uow=self.uow, location='Almaty')
        self.assertEqual(result, expected)

    def test_list_events_service_should_return_list_of_events_by_tags(self):
        for i in range(3):
            event = self.uow.event.create(**{
                "name": "test_event",
                "image": 'test_image',
                "location": 'Almaty',
                "location_url": 'https://www.google.com',
                "description": 'Test description',
                "full_description": 'Test full description',
                "start_date": '2020-01-01',
                "end_date": '2020-01-02',
                "author": self.user,
                "tags": ['test_tag1', 'test_tag2'],
            })
        for i in range(3):
            event = self.uow.event.create(**{
                "name": "test_event",
                "image": 'test_image',
                "location": 'Qostanay',
                "location_url": 'https://www.google.com',
                "description": 'Test description',
                "full_description": 'Test full description',
                "start_date": '2020-01-01',
                "end_date": '2020-01-02',
                "author": self.user,
                "tags": ['test_tag3', 'test_tag4'],
            })
        expected = Result(data=[
            event.to_dict() for event in self.uow.event.list(tags__contains='test_tag3')
        ], error=None)
        result = services.list_events_service(
            uow=self.uow,  tags__contains='test_tag3')
        self.assertEqual(result, expected)

    def test_list_events_service_should_return_list_of_active_events_when_no_params_passed(self):
        for i in range(5):
            self.uow.event.create(**{
                "name": "test_event",
                "image": 'test_image',
                "location": 'Almaty',
                "location_url": 'https://www.google.com',
                "description": 'Test description',
                "full_description": 'Test full description',
                "start_date": '2020-01-01',
                "end_date": '2020-01-02',
                "author": self.user,
                "tags": ['test_tag1', 'test_tag2'],
            })
        for i in range(5):
            event = self.uow.event.create(**{
                "name": "test_event",
                "image": 'test_image',
                "location": 'Qostanay',
                "location_url": 'https://www.google.com',
                "description": 'Test description',
                "full_description": 'Test full description',
                "start_date": '2020-01-01',
                "is_active": False,
                "end_date": '2020-01-02',
                "author": self.user,
                "tags": ['test_tag3', 'test_tag4'],
            })
        expected = Result(data=[
            event.to_dict() for event in self.uow.event.list()
        ], error=None)
        result = services.list_events_service(
            uow=self.uow)
        self.assertEqual(result, expected)
        self.assertEqual(len(result.data), 5)

    def test_list_events_service_should_return_list_of_user_events_by_user(self):
        my_user = self.uow.user.create(username="my_user", password="my_user")
        for i in range(5):
            self.uow.event.create(**{
                "name": "test_event",
                "image": 'test_image',
                "location": 'Almaty',
                "location_url": 'https://www.google.com',
                "description": 'Test description',
                "full_description": 'Test full description',
                "start_date": '2020-01-01',
                "end_date": '2020-01-02',
                "author": my_user,
                "tags": ['test_tag1', 'test_tag2'],
            })
        for i in range(5):
            self.uow.event.create(**{
                "name": "test_event",
                "image": 'test_image',
                "location": 'Qostanay',
                "location_url": 'https://www.google.com',
                "description": 'Test description',
                "full_description": 'Test full description',
                "start_date": '2020-01-01',
                "is_active": False,
                "end_date": '2020-01-02',
                "author": self.user,
                "tags": ['test_tag3', 'test_tag4'],
            })
        expected = Result(data=[event.to_dict() for event in self.uow.event.list(
            author=my_user)], error=None)
        result = services.list_events_service(
            uow=self.uow, author=my_user)
        self.assertEqual(result, expected)
        self.assertEqual(len(result.data), 5)

    # Create event
    def test_create_event_service_should_return_event(self):
        expected = Result(data={
            "id": 1,
            "name": "test_event",
            "image": 'test_image',
            "location": 'Almaty',
            "location_url": 'https://www.google.com',
            "description": 'Test description',
            "full_description": 'Test full description',
            "start_date": '2020-01-01',
            "end_date": '2020-01-02',
            "author": self.user.to_dict(),
            "tags": ['test_tag1', 'test_tag2'],
            "is_active": True,
        }, error=None)
        result = services.create_event_service(uow=self.uow, username=self.user.username, **{
            "name": "test_event",
            "image": 'test_image',
            "location": 'Almaty',
            "location_url": 'https://www.google.com',
            "description": 'Test description',
            "full_description": 'Test full description',
            "start_date": '2020-01-01',
            "end_date": '2020-01-02',
            "tags": ['test_tag1', 'test_tag2'],
        })
        self.assertEqual(result, expected)

    def test_create_event_service_should_return_result_with_error_when_data_is_invalid(self):
        expected = Result(
            data=None, error=exceptions.InvalidEventDataException)
        result = services.create_event_service(uow=self.uow, username=self.user.username, **{
            "name": "",
            "image": 'test_image',
            "location": 'Almaty',
            "location_url": 'https://www.google.com',
            "description": 'Test description',
            "full_description": 'Test full description',
            "start_date": '2020-01-01',
            "end_date": '2020-01-02',
            "tags": ['test_tag1', 'test_tag2'],
        })
        self.assertEqual(result, expected)

    # Edit event

    def test_edit_event_service_should_return_event(self):
        self.uow.event.create(**{
            "name": "test_event",
            "image": 'test_image',
            "location": 'Almaty',
            "location_url": 'https://www.google.com',
            "description": 'Test description',
            "full_description": 'Test full description',
            "start_date": '2020-01-01',
            "end_date": '2020-01-02',
            "author": self.user,
            "tags": ['test_tag1', 'test_tag2'],
        })
        expected = Result(data={
            "id": 1,
            "name": "test_event updated",
            "image": 'test_image',
            "location": 'Almaty',
            "location_url": 'https://www.google.com',
            "description": 'Test description',
            "full_description": 'Test full description',
            "start_date": '2020-11-01',
            "end_date": '2020-11-02',
            "author": self.user.to_dict(),
            "tags": ['test_tag1', 'test_tag2'],
            "is_active": True,
        }, error=None)
        result = services.edit_event_service(uow=self.uow, id=1, username=self.user.username, **{
            "name": "test_event updated",
            "image": 'test_image',
            "location": 'Almaty',
            "location_url": 'https://www.google.com',
            "description": 'Test description',
            "full_description": 'Test full description',
            "start_date": '2020-11-01',
            "end_date": '2020-11-02',
            "author": self.user,
            "tags": ['test_tag1', 'test_tag2'],
        })
        self.assertEqual(result, expected)

    def test_edit_event_service_should_return_result_with_error_when_data_is_invalid(self):
        self.uow.event.create(**{
            "name": "test_event",
            "image": 'test_image',
            "location": 'Almaty',
            "location_url": 'https://www.google.com',
            "description": 'Test description',
            "full_description": 'Test full description',
            "start_date": '2020-01-01',
            "end_date": '2020-01-02',
            "author": self.user,
            "tags": ['test_tag1', 'test_tag2'],
        })
        expected = Result(
            data=None, error=exceptions.InvalidEventDataException)
        result = services.edit_event_service(uow=self.uow, id=1, username=self.user.username, **{
            "name": "",
            "image": 'test_image',
            "location": 'Almaty',
            "location_url": 'https://www.google.com',
            "description": 'Test description',
            "full_description": 'Test full description',
            "start_date": '2020-11-01',
            "end_date": '2020-11-02',
            "author": self.user,
            "tags": ['test_tag1', 'test_tag2'],
        })
        self.assertEqual(result, expected)

    def test_edit_event_service_should_return_result_with_error_when_event_is_not_found(self):
        expected = Result(data=None, error=exceptions.EventNotFoundException)
        result = services.edit_event_service(uow=self.uow, id=999, username=self.user.username, **{
            "name": "test_event updated",
            "image": 'test_image',
            "location": 'Almaty',
            "location_url": 'https://www.google.com',
            "description": 'Test description',
            "full_description": 'Test full description',
            "start_date": '2020-11-01',
            "end_date": '2020-11-02',
            "author": self.user,
            "tags": ['test_tag1', 'test_tag2'],
        })
        self.assertEqual(result, expected)

    def test_edit_event_service_should_return_result_with_error_when_user_is_not_author(self):
        another_user = self.uow.user.create(
            username="another_user", password="test")
        self.uow.event.create(**{
            "name": "test_event",
            "image": 'test_image',
            "location": 'Almaty',
            "location_url": 'https://www.google.com',
            "description": 'Test description',
            "full_description": 'Test full description',
            "start_date": '2020-01-01',
            "end_date": '2020-01-02',
            "author": another_user,
            "tags": ['test_tag1', 'test_tag2'],
        })
        expected = Result(
            data=None, error=exceptions.UserIsNotEventAuthorException)
        result = services.edit_event_service(uow=self.uow, id=1, username=self.user.username, **{
            "name": "test_event updated",
            "image": 'test_image',
            "location": 'Almaty',
            "location_url": 'https://www.google.com',
            "description": 'Test description',
            "full_description": 'Test full description',
            "start_date": '2020-11-01',
            "end_date": '2020-11-02',
            "author": self.user,
            "tags": ['test_tag1', 'test_tag2'],
        })
        self.assertEqual(result, expected)

    def test_deactivate_event_service_should_deactivate_event(self):
        self.uow.event.create(**{
            "name": "test_event",
            "image": 'test_image',
            "location": 'Almaty',
            "location_url": 'https://www.google.com',
            "description": 'Test description',
            "full_description": 'Test full description',
            "start_date": '2020-01-01',
            "end_date": '2020-01-02',
            "author": self.user,
            "tags": ['test_tag1', 'test_tag2'],
        })
        expected = Result(data={
            "id": 1,
            "name": "test_event",
            "image": 'test_image',
            "location": 'Almaty',
            "location_url": 'https://www.google.com',
            "description": 'Test description',
            "full_description": 'Test full description',
            "start_date": '2020-01-01',
            "end_date": '2020-01-02',
            "author": self.user.to_dict(),
            "tags": ['test_tag1', 'test_tag2'],
            "is_active": False,
        }, error=None)
        result = services.deactivate_event_service(
            uow=self.uow, id=1, username=self.user.username)
        self.assertEqual(result, expected)

    def test_deactivate_event_service_should_return_error_when_event_is_not_found(self):
        expected = Result(data=None, error=exceptions.EventNotFoundException)
        result = services.deactivate_event_service(
            uow=self.uow, id=999, username=self.user.username)
        self.assertEqual(result, expected)

    def test_deactivate_event_service_should_return_error_when_user_is_not_author(self):
        another_user = self.uow.user.create(
            username="another_user", password="test")
        self.uow.event.create(**{
            "name": "test_event",
            "image": 'test_image',
            "location": 'Almaty',
            "location_url": 'https://www.google.com',
            "description": 'Test description',
            "full_description": 'Test full description',
            "start_date": '2020-01-01',
            "end_date": '2020-01-02',
            "author": another_user,
            "tags": ['test_tag1', 'test_tag2'],
        })
        expected = Result(
            data=None, error=exceptions.UserIsNotEventAuthorException)
        result = services.deactivate_event_service(
            uow=self.uow, id=1, username=self.user.username)
        self.assertEqual(result, expected)


@override_settings(DEBUG=True)
class TestMessageBrokerServices(TestCase):
    def setUp(self) -> None:
        self.uow = uow.FakeUnitOfWork()
        self.user = self.uow.user.create(username="test", password="test")
        return super().setUp()

    def test_create_event_service_should_publish_message_on_success(self):
        q = 'test.services.create.q'
        message_broker = mb.RabbitMQ(
            exchange=settings.RABBITMQ_TEST_EXCHANGE_NAME)
        with message_broker:
            message_broker.channel.queue_declare(
                queue=q, durable=True, exclusive=True)
            message_broker.channel.queue_bind(exchange=settings.RABBITMQ_TEST_EXCHANGE_NAME,
                                              queue=q, routing_key=settings.RABBITMQ_EVENT_CREATE_ROUTING_KEY)
            message = {
                "id": 1,
                "name": "test_event",
                "image": 'test_image',
                "location": 'Almaty',
                "location_url": 'https://www.google.com',
                "description": 'Test description',
                "full_description": 'Test full description',
                "start_date": '2020-01-01',
                "end_date": '2020-01-02',
                "author": self.user.to_dict(),
                "tags": ['test_tag1', 'test_tag2'],
                "is_active": True,
            }
            services.create_event_service(uow=self.uow, username=self.user.username, **{
                "name": "test_event",
                "image": 'test_image',
                "location": 'Almaty',
                "location_url": 'https://www.google.com',
                "description": 'Test description',
                "full_description": 'Test full description',
                "start_date": '2020-01-01',
                "end_date": '2020-01-02',
                "tags": ['test_tag1', 'test_tag2'],
            })
            method, properties, body = message_broker.channel.basic_get(
                queue=q, auto_ack=True)
            self.assertEqual(json.loads(body), message)

    def test_edit_event_service_should_publish_message_on_success(self):
        q = 'test.services.edit.q'
        message_broker = mb.RabbitMQ(
            exchange=settings.RABBITMQ_TEST_EXCHANGE_NAME)
        with message_broker:
            message_broker.channel.queue_declare(
                queue=q, durable=True, exclusive=True)
            message_broker.channel.queue_bind(exchange=settings.RABBITMQ_TEST_EXCHANGE_NAME,
                                              queue=q, routing_key=settings.RABBITMQ_EVENT_EDIT_ROUTING_KEY)
            self.uow.event.create(**{
                "name": "test_event",
                "image": 'test_image',
                "location": 'Almaty',
                "location_url": 'https://www.google.com',
                "description": 'Test description',
                "full_description": 'Test full description',
                "start_date": '2020-01-01',
                "end_date": '2020-01-02',
                "author": self.user,
                "tags": ['test_tag1', 'test_tag2'],
            })
            message = {
                "id": 1,
                "name": "test_event updated",
                "image": 'test_image',
                "location": 'Almaty',
                "location_url": 'https://www.google.com',
                "description": 'Test description',
                "full_description": 'Test full description',
                "start_date": '2020-11-01',
                "end_date": '2020-11-02',
                "author": self.user.to_dict(),
                "tags": ['test_tag1', 'test_tag2'],
                "is_active": True,
            }
            services.edit_event_service(uow=self.uow, id=1, username=self.user.username, **{
                "name": "test_event updated",
                "image": 'test_image',
                "location": 'Almaty',
                "location_url": 'https://www.google.com',
                "description": 'Test description',
                "full_description": 'Test full description',
                "start_date": '2020-11-01',
                "end_date": '2020-11-02',
                "author": self.user,
                "tags": ['test_tag1', 'test_tag2'],
            })
            method, properties, body = message_broker.channel.basic_get(
                queue=q, auto_ack=True)
            self.assertEqual(json.loads(body), message)

    def test_deactivate_event_service_should_publish_message_on_success(self):
        q = 'test.services.deactivate.q'
        message_broker = mb.RabbitMQ(
            exchange=settings.RABBITMQ_TEST_EXCHANGE_NAME)
        with message_broker:
            message_broker.channel.queue_declare(
                queue=q, durable=True, exclusive=True)
            message_broker.channel.queue_bind(exchange=settings.RABBITMQ_TEST_EXCHANGE_NAME,
                                              queue=q, routing_key=settings.RABBITMQ_EVENT_EDIT_ROUTING_KEY)
            self.uow.event.create(**{
                "name": "test_event",
                "image": 'test_image',
                "location": 'Almaty',
                "location_url": 'https://www.google.com',
                "description": 'Test description',
                "full_description": 'Test full description',
                "start_date": '2020-01-01',
                "end_date": '2020-01-02',
                "author": self.user,
                "tags": ['test_tag1', 'test_tag2'],
            })
            message = {
                "id": 1,
                "name": "test_event",
                "image": 'test_image',
                "location": 'Almaty',
                "location_url": 'https://www.google.com',
                "description": 'Test description',
                "full_description": 'Test full description',
                "start_date": '2020-01-01',
                "end_date": '2020-01-02',
                "author": self.user.to_dict(),
                "tags": ['test_tag1', 'test_tag2'],
                "is_active": False,
            }
            services.deactivate_event_service(
                uow=self.uow, id=1, username=self.user.username)
            method, properties, body = message_broker.channel.basic_get(
                queue=q, auto_ack=True)
            self.assertEqual(json.loads(body), message)
