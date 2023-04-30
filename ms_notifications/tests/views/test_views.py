import json
from django.test import TransactionTestCase, override_settings
from rest_framework.test import APIClient as Client
from django.core.files.uploadedfile import SimpleUploadedFile


import service_layer.unit_of_work as uow
import core.exceptions as exceptions
import core.constants as constants

import shutil


def create_user(username="test@gmail.com", password="testpassword", first_name="test", last_name="user"):
    django_uow = uow.DjangoORMUnitOfWork()
    with django_uow:
        user = django_uow.user.create(
            email=username,
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password
        )
        return user


def create_notification(user, status=constants.SUCCESS_TYPE, message='test_message'):
    django_uow = uow.DjangoORMUnitOfWork()
    with django_uow:
        notification = django_uow.notifications.create(
            user=user, status=status, message=message)
        return notification


class TestNotificationManagement(TransactionTestCase):
    reset_sequences = True

    def setUp(self) -> None:
        self.client = Client()
        self.user = create_user()

    def test_get_notification_should_return_notification_data(self):
        notification = create_notification(user=self.user)
        token = self.user.generate_jwt_token()
        response = self.client.get(
            f"/notifications/{notification.id}/",  **{"HTTP_AUTHORIZATION": f"Bearer {token}"}, )
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content['data'], notification.to_dict())
        self.assertEqual(content['error'], None)

    def test_list_notification_should_return_notification_data(self):
        notifications = []
        for _ in range(5):
            notification = create_notification(user=self.user)
            notifications.append(notification)
            token = self.user.generate_jwt_token()
        response = self.client.get(
            f"/notifications/", **{"HTTP_AUTHORIZATION": f"Bearer {token}"})
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content['data'], [notif.to_dict()
                         for notif in notifications])
        self.assertEqual(content['error'], None)
