
import service_layer.unit_of_work as uow
from service_layer.result import Result
import core.exceptions as exceptions


def get_event_service(uow: uow.AbstractUnitOfWork, id: int):
    with uow:
        event = uow.event.get(id=id)
        if event is None:
            return Result(data=None, error=exceptions.EventNotFoundException)
        return Result(data=event.to_dict(), error=None)


def list_events_service(uow: uow.AbstractUnitOfWork, **kwargs):
    with uow:
        events = uow.event.list(**kwargs)
        return Result(data=[event.to_dict() for event in events], error=None)


def create_event_service(uow: uow.AbstractUnitOfWork, username, **kwargs):
    with uow:
        if not kwargs.get('name'):
            return Result(data=None, error=exceptions.InvalidEventDataException)
        user = uow.user.get(username=username)
        event = uow.event.create(author=user, **kwargs)
        try:
            handle_publish_message_on_event_created(event)
        except Exception as e:
            print(e)
        return Result(data=event.to_dict(), error=None)


def edit_event_service(uow: uow.AbstractUnitOfWork, id: int, username: str, **kwargs):
    with uow:
        if not kwargs.get('name'):
            return Result(data=None, error=exceptions.InvalidEventDataException)
        event = uow.event.get(id=id)
        if event is None:
            return Result(data=None, error=exceptions.EventNotFoundException)
        user = uow.user.get(username=username)
        if event.author != user:
            return Result(data=None, error=exceptions.UserIsNotEventAuthorException)
        event = uow.event.edit(id=id, **kwargs)
        try:
            handle_publish_message_on_event_edited(event)
        except Exception as e:
            print(e)
        return Result(data=event.to_dict(), error=None)


def deactivate_event_service(uow: uow.AbstractUnitOfWork, id: int, username: str):
    with uow:
        event = uow.event.get(id=id)
        if event is None:
            return Result(data=None, error=exceptions.EventNotFoundException)
        user = uow.user.get(username=username)
        if event.author != user:
            return Result(data=None, error=exceptions.UserIsNotEventAuthorException)
        event = uow.event.deactivate(id=id)
        try:
            handle_publish_message_on_event_edited(event)
        except Exception as e:
            print(e)
        return Result(data=event.to_dict(), error=None)


def handle_publish_message_on_event_created(event):
    import pika
    import json
    from django.conf import settings
    import services.message_broker as mb
    credentials = pika.URLParameters(settings.RABBITMQ_CONNECTION_URL)
    message_broker = mb.RabbitMQ(
        credentials.host, credentials.port, credentials.credentials.username, credentials.credentials.password, exchange=settings.RABBITMQ_EXCHANGE_NAME)
    print('Connecting to message broker...')
    with message_broker:
        print('Publishing message...')
        message_broker.publish(
            message=json.dumps(event.to_dict()), routing_key=settings.RABBITMQ_EVENT_CREATE_ROUTING_KEY)


def handle_publish_message_on_event_edited(event):
    import pika
    import json
    from django.conf import settings
    import services.message_broker as mb
    credentials = pika.URLParameters(settings.RABBITMQ_CONNECTION_URL)
    message_broker = mb.RabbitMQ(
        credentials.host, credentials.port, credentials.credentials.username, credentials.credentials.password, exchange=settings.RABBITMQ_EXCHANGE_NAME)
    print('Connecting to message broker...')
    with message_broker:
        print('Publishing message...')
        message_broker.publish(
            message=json.dumps(event.to_dict()), routing_key=settings.RABBITMQ_EVENT_EDIT_ROUTING_KEY)
