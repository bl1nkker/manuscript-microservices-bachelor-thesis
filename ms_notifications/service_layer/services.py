import json
from django.conf import settings
import service_layer.unit_of_work as uow
from service_layer.result import Result
import core.exceptions as exceptions
import core.logger as logger
import core.constants as constants


def get_notification_service(uow: uow.AbstractUnitOfWork, username: str, id: int) -> Result:
    with uow:
        notification = uow.notifications.get(id=id)
        if notification is None:
            return Result(data=None, error=exceptions.NotificationNotFoundException)
        user = uow.user.get(username=username)
        if notification.user != user:
            return Result(data=None, error=exceptions.UserIsNotNotificationOwnerException)
        return Result(data=notification.to_dict(), error=None)


def list_notifications_service(uow: uow.AbstractUnitOfWork, username: str) -> Result:
    with uow:
        user = uow.user.get(username=username)
        notifications = uow.notifications.list(user=user)
        return Result(data=[notif.to_dict() for notif in notifications], error=None)
