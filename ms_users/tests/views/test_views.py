import json

from django.test import TestCase, Client, override_settings

import service_layer.unit_of_work as uow
import core.exceptions as exceptions
# import app.core.failures_messages as failure_messages


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


@override_settings(DEBUG=True)
class TestAuthentication(TestCase):
    def setUp(self):
        self.client = Client()

    def test_user_sign_in_should_return_token(self):
        create_user(username="test@gmail.com", password="testpassword",
                    first_name="test", last_name="user")
        body = {
            "email": "test@gmail.com",
            "password": "testpassword"
        }
        response = self.client.post(
            "/signin/", data=body)
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertIsNotNone(content['data']['access_token'])

    def test_user_sign_in_should_return_error_when_password_is_incorrect(self):
        create_user(username="test@gmail.com", password="testpassword",
                    first_name="test", last_name="user")
        body = {
            "email": "test@gmail.com",
            "password": "incorrect_password"
        }
        response = self.client.post(
            "/signin/", data=body)
        self.assertEqual(response.status_code, 401)
        content = json.loads(response.content)
        self.assertEqual(content['error'],
                         exceptions.AUTHENTICATION_EXCEPTION_MESSAGE)

    def test_user_sign_in_should_return_error_when_user_is_not_found(self):
        body = {
            "email": "test@gmail.com",
            "password": "testpassword"
        }
        response = self.client.post(
            "/signin/", data=body)
        self.assertEqual(response.status_code, 401)
        content = json.loads(response.content)
        self.assertEqual(content['error'],
                         exceptions.AUTHENTICATION_EXCEPTION_MESSAGE)

    def test_sign_up_should_return_result_token(self):
        body = {
            "email": "test@gmail.com",
            "first_name": "Test",
            "last_name": "User",
            "password": "test1234",
            "confirm_password": "test1234",
        }
        response = self.client.post(
            "/signup/", data=body)
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertIsNotNone(content['data']['access_token'])

    def test_sign_up_should_return_error_when_validation_error_occured(self):
        body = {
            "email": "",
            "first_name": "",
            "last_name": "",
            "password": "test1234",
            "confirm_password": "test1234",
        }
        response = self.client.post(
            "/signup/", data=body)
        self.assertEqual(response.status_code, 401)
        content = json.loads(response.content)
        self.assertEqual(content['message'],
                         exceptions.INVALID_USER_DATA_EXCEPTION_MESSAGE)

    def test_sign_up_should_return_error_when_password_doesnt_match(self):
        body = {
            "email": "test@gmail.com",
            "first_name": "Test",
            "last_name": "User",
            "password": "test1234",
            "confirm_password": "another_password",
        }
        response = self.client.post(
            "/signup/", data=body)
        self.assertEqual(response.status_code, 401)
        content = json.loads(response.content)
        self.assertEqual(content['message'],
                         exceptions.INVALID_USER_DATA_EXCEPTION_MESSAGE)


class TestUserGet(TestCase):
    def setUp(self) -> None:
        self.user = create_user()
        return super().setUp()

    # Get User
    def test_get_user_should_return_user_data(self):
        response = self.client.get(f"/users/{self.user.id}")
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content, self.user.to_dict())

    def test_get_user_should_returnerror_when_user_is_not_found(self):
        response = self.client.get(f"/users/999")
        self.assertEqual(response.status_code, 404)
        content = json.loads(response.content)
        self.assertEqual(content['message'],
                         exceptions.USER_NOT_FOUND_EXCEPTION_MESSAGE)

    def test_get_me_should_return_user_data(self):
        token = self.user.generate_jwt_token()
        response = self.client.get(
            "/me/", **{"HTTP_AUTHORIZATION": f"Bearer {token}"})
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content, self.user.to_dict())

    def test_get_me_should_return_error_when_user_is_not_authenticated(self):
        response = self.client.get(
            "/me/", **{"HTTP_AUTHORIZATION": f"Bearer 123"})
        self.assertEqual(response.status_code, 403)
