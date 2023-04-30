from django.test import TestCase

from service_layer.result import Result
import service_layer.services as services
import service_layer.unit_of_work as uow
import core.constants as constants
import core.exceptions as exceptions


class TestNotificationServices(TestCase):

    def setUp(self) -> None:
        self.uow = uow.FakeUnitOfWork()
        self.user = self.uow.user.create(username="test", password="test")
        return super().setUp()

    def create_notification(self, user=None, status=constants.SUCCESS_TYPE):
        if user is None:
            user = self.user
        return self.uow.notifications.create(
            user=user, status=status, message='test_message')

    def test_get_notification_service_should_return_result_with_notification(self):
        notification = self.create_notification()
        expected = Result(data=notification.to_dict(), error=None)
        result = services.get_notification_service(
            uow=self.uow, username=self.user.username, id=notification.id)
        self.assertEqual(result, expected)

    def test_get_notification_service_should_return_result_with_error_when_notification_is_not_found(self):
        expected = Result(
            data=None, error=exceptions.NotificationNotFoundException)
        result = services.get_notification_service(
            uow=self.uow, username=self.user.username, id=999)
        self.assertEqual(result, expected)

    def test_get_notification_service_should_return_result_with_error_when_user_is_not_owner_of_notification(self):
        notification = self.create_notification()
        expected = Result(
            data=None, error=exceptions.UserIsNotNotificationOwnerException)
        another_user = self.uow.user.create(
            username="another", password="another")
        result = services.get_notification_service(
            uow=self.uow, username=another_user.username, id=notification.id)
        self.assertEqual(result, expected)

    def test_list_notifications_service_should_return_list_of_notifications(self):
        notifications = []
        for _ in range(3):
            notif = self.create_notification(
                status=constants.SUCCESS_TYPE)
            notifications.append(notif)
        another_user = self.uow.user.create(
            username="another", password="another")
        for _ in range(3):
            self.create_notification(
                user=another_user, status=constants.SUCCESS_TYPE)
        expected = Result(data=[
            notif.to_dict() for notif in notifications], error=None)
        result = services.list_notifications_service(
            uow=self.uow, username=self.user.username)
        self.assertEqual(result, expected)
