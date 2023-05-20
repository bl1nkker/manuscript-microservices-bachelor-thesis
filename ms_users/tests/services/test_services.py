import json
from django.test import TransactionTestCase, TestCase, override_settings
from django.conf import settings

import service_layer.unit_of_work as uow
import service_layer.services as services
import core.exceptions as exceptions
from service_layer import Result
import service_layer.message_broker as mb


@override_settings(DEBUG=True)
class TestUserServices(TransactionTestCase):
    def setUp(self) -> None:
        self.uow = uow.FakeUnitOfWork()
        return super().setUp()

    # @patch('services.services')
    def test_sign_in_user_service_should_return_result_with_access_token(self):
        self.uow.user.create(username="test", password="test")
        expected = Result(data={"access_token": 'test_token'}, error=None)
        result = services.sign_in_user_service(
            uow=self.uow, request=None, username="test", password="test")
        self.assertEqual(expected, result)

    def test_sign_in_user_service_should_return_result_with_error_when_password_is_incorrect(self):
        self.uow.user.create(username="test", password="test")
        expected = Result(data=None, error=exceptions.AuthenticationException)
        result = services.sign_in_user_service(
            uow=self.uow, request=None, username="test", password="incorrect_password")
        self.assertEqual(expected, result)

    def test_sign_in_user_service_should_return_result_with_error_when_user_is_not_found(self):
        expected = Result(data=None, error=exceptions.AuthenticationException)
        result = services.sign_in_user_service(
            uow=self.uow, request=None, username="test", password="test")
        self.assertEqual(expected, result)

    def test_sign_up_user_service_should_return_result_with_user_and_token(self):
        expected = Result(data={"access_token": 'test_token'}, error=None)
        result = services.sign_up_user_service(
            uow=self.uow, request=None, username="test", password="test", confirm_password="test", first_name="test", last_name="user")
        self.assertEqual(expected, result)

    def test_sign_up_user_service_should_return_result_with_error_when_validation_error_occured(self):
        expected = Result(data=None, error=exceptions.InvalidUserDataException)
        result = services.sign_up_user_service(
            uow=self.uow, request=None, username="", password="test", confirm_password="test", first_name="", last_name="")
        self.assertEqual(expected, result)

    def test_sign_up_user_service_should_return_result_with_error_when_password_doesnt_match(self):
        expected = Result(data=None, error=exceptions.InvalidUserDataException)
        result = services.sign_up_user_service(
            uow=self.uow, request=None, username="test", password="test", confirm_password="test123", first_name="test", last_name="user")
        self.assertEqual(expected, result)

    # Get User
    def test_get_user_service_should_return_result_with_user_data(self):
        user = self.uow.user.create(username="test", password="test")
        expected = Result(data=user.to_dict(), error=None)
        result = services.get_user_service(uow=self.uow, uid=user.id)
        self.assertEqual(expected, result)

    def test_get_user_service_should_return_result_with_error_when_user_is_not_found(self):
        expected = Result(data=None, error=exceptions.UserNotFoundException)
        result = services.get_user_service(uow=self.uow, uid=999)
        self.assertEqual(expected, result)

    # Get Me

    def test_get_me_service_should_return_result_with_user_data(self):
        user = self.uow.user.create(username="test", password="test")
        expected = Result(data=user.to_dict(), error=None)
        result = services.get_me_service(uow=self.uow, user=user)
        self.assertEqual(expected, result)
