
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
        return Result(data=event.to_dict(), error=None)
