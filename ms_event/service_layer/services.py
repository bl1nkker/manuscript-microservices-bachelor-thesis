import json
from django.conf import settings
import service_layer.message_broker as mb
import service_layer.unit_of_work as uow
from service_layer.result import Result
import core.exceptions as exceptions
import core.logger as logger


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


def create_event_service(uow: uow.AbstractUnitOfWork, username, **kwargs, ):
    with uow:
        if not kwargs.get('name'):
            return Result(data=None, error=exceptions.InvalidEventDataException)
        user = uow.user.get(username=username)
        event = uow.event.create(author=user, **kwargs)
        handle_publish_message_on_event_created(data=event.to_dict())
        return Result(data=event.to_dict(), error=None)


def edit_event_service(uow: uow.AbstractUnitOfWork, id: int, username: str, **kwargs, ):
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
        handle_publish_message_on_event_edited(data=event.to_dict())
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
        handle_publish_message_on_event_edited(data=event.to_dict())
        return Result(data=event.to_dict(), error=None)


def handle_publish_message_on_event_created(data):
    try:
        if settings.DEBUG:
            message_broker = mb.RabbitMQ(
                exchange=settings.RABBITMQ_TEST_EXCHANGE_NAME)
        else:
            message_broker = mb.RabbitMQ()
        with message_broker:
            message_broker.publish(
                message=json.dumps(data), routing_key=settings.RABBITMQ_EVENT_CREATE_ROUTING_KEY)
        logger.info(user='PUBLISHER',
                    message=f'Data({data}) sent to {settings.RABBITMQ_EVENT_CREATE_ROUTING_KEY}', logger=logger.mb_logger)
    except Exception as e:
        logger.error(
            user='PUBLISHER', message=f'Error while publishing message on event created: {e}', logger=logger.mb_logger)


def handle_publish_message_on_event_edited(data):
    try:
        if settings.DEBUG:
            message_broker = mb.RabbitMQ(
                exchange=settings.RABBITMQ_TEST_EXCHANGE_NAME)
        else:
            message_broker = mb.RabbitMQ()

        with message_broker:
            message_broker.publish(
                message=json.dumps(data), routing_key=settings.RABBITMQ_EVENT_EDIT_ROUTING_KEY)
        logger.info(user='PUBLISHER',
                    message=f'Data({data}) sent to {settings.RABBITMQ_EVENT_EDIT_ROUTING_KEY}', logger=logger.mb_logger)
    except Exception as e:
        logger.error(
            user='PUBLISHER', message=f'Error while publishing message on event edited: {e}', logger=logger.mb_logger)
