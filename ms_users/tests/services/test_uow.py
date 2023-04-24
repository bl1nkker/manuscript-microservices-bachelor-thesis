from django.test import TransactionTestCase
from django.contrib.auth import authenticate

import app.models as models
import service_layer.unit_of_work as uow


class TestDjangoORMUnitOfWork(TransactionTestCase):
    reset_sequences = True

    def setUp(self) -> None:
        self.uow = uow.DjangoORMUnitOfWork()

    def test_user_repository_create_user_should_create_user(self):
        with self.uow:
            self.uow.user.create(
                username="test@gmail.com", email="test@gmail.com", first_name="test", last_name="user", password='testpassword')
            self.assertEqual(1, models.ManuscriptUser.objects.count())
            self.assertEqual(1, models.User.objects.count())
            self.assertEqual(
                "test@gmail.com", models.ManuscriptUser.objects.first().user.username)
            self.assertEqual(
                "test@gmail.com", models.ManuscriptUser.objects.first().user.email)
            self.assertEqual(
                "test", models.ManuscriptUser.objects.first().user.first_name)
            self.assertEqual(
                "user", models.ManuscriptUser.objects.first().user.last_name)
            self.assertEqual(authenticate(username='test@gmail.com', password='testpassword'),
                             models.ManuscriptUser.objects.first().user)

    def test_user_repository_get_user_should_return_user(self):
        with self.uow:
            self.uow.user.create(username="test")
            result = self.uow.user.get(username="test")
            self.assertEqual(result.user.username, 'test')
            result = self.uow.user.get(id=1)
            self.assertEqual(result.user.id, 1)

    def test_user_repository_get_user_should_return_none_when_user_is_not_found(self):
        with self.uow:
            result = self.uow.user.get(username="test_user")
            self.assertEqual(None, result)
