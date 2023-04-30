import app.models as models
import service_layer.unit_of_work as uow
from django.test import TransactionTestCase
from django.core.files.uploadedfile import SimpleUploadedFile
import core.constants as constants


class TestDjangoORMUnitOfWork(TransactionTestCase):
    reset_sequences = True

    def setUp(self) -> None:
        self.uow = uow.DjangoORMUnitOfWork()
        user = models.User.objects.create(username='test_user')
        self.user = models.ManuscriptUser.objects.create(user=user)
        return super().setUp()

    # Create
    def test_notification_repository_create_should_create_notification(self):
        with self.uow:
            data = {
                "user": self.user,
                "message": 'Test message',
                "status": constants.SUCCESS_TYPE,
            }
            event = self.uow.notifications.create(**data)
            self.assertEqual(1, models.Notification.objects.count())
            self.assertEqual(event.message, 'Test message')
            self.assertEqual(event.status, constants.SUCCESS_TYPE)
            self.assertEqual(event.user, self.user)

    # List

    def test_event_repository_list_should_list_active_events(self):
        with self.uow:
            user = models.User.objects.create(username='sdfs')
            another_user = models.ManuscriptUser.objects.create(user=user)
            for _ in range(5):
                data = {
                    "user": self.user,
                    "message": 'Test message',
                    "status": constants.SUCCESS_TYPE,
                }
                self.uow.notifications.create(**data)
                data = {
                    "user": another_user,
                    "message": 'Test message',
                    "status": constants.SUCCESS_TYPE,
                }
                self.uow.notifications.create(**data)
            for _ in range(3):
                data = {
                    "user": self.user,
                    "message": 'Test message',
                    "status": constants.WARNING_TYPE,
                }
                self.uow.notifications.create(**data)
            events = self.uow.notifications.list(
                status=constants.SUCCESS_TYPE, user=self.user)
            self.assertEqual(5, len(events))

    # Get

    def test_event_repository_get_should_get_event(self):
        with self.uow:
            for i in range(3):
                data = {
                    "user": self.user,
                    "message": 'Test message',
                    "status": constants.SUCCESS_TYPE,
                }
                self.uow.notifications.create(**data)
            notification = self.uow.notifications.get(id=1)
            self.assertEqual(notification.id, 1)
            self.assertEqual(notification.message, 'Test message')
            notification = self.uow.notifications.get(id=2)
            self.assertEqual(notification.id, 2)
            self.assertEqual(notification.message, 'Test message')
