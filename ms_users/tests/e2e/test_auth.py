import json

from django.test import TestCase, Client
import app.models as models


class TestAuth(TestCase):

    def setUp(self) -> None:
        self.client = Client()
        return super().setUp()

    def test_register_should_return_user_data_and_token(self):
        body = {
            "email": "test@gmail.com",
            "first_name": "Test",
            "last_name": "User",
            "password": "test1234",
        }
        response = self.client.post(
            "/register/", body, content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(models.User.objects.count(), 1)
        content = json.loads(response.content)
        user = models.ManuscriptUser.objects.get(user__email=body['email'])
        self.assertEqual(content['user'], user.to_dict())
        assert content['token'] is not None

    def test_login_should_return_user_data_and_token(self):
        user = models.User.objects.create(
            email="test@gmail.com",
            username="test@gmail.com",
            first_name="Test",
            last_name="User",
        )
        user.set_password("test1234")
        user.save()
        models.ManuscriptUser.objects.create(user=user)
        body = {
            "email": "test@gmail.com",
            "password": "test1234"
        }
        response = self.client.post(
            "/login/", body, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        user = models.ManuscriptUser.objects.get(user__email=body['email'])
        self.assertEqual(content['user'], user.to_dict())
        assert content['token'] is not None

    def test_get_users_should_get_users_when_user_is_authenticated(self):
        user = models.User.objects.create(
            email="test@gmail.com",
            username="test@gmail.com",
            first_name="Test",
            last_name="User",
        )
        user.set_password("test1234")
        user.save()
        m_user = models.ManuscriptUser.objects.create(user=user)
        token = m_user.generate_jwt_token()
        response = self.client.get(
            "/users/", **{"HTTP_AUTHORIZATION": f"Bearer {token}"})
        self.assertEqual(response.status_code, 200)

    def test_get_users_should_return_error_when_user_is_not_authenticated(self):
        response = self.client.get("/users/")
        self.assertEqual(response.status_code, 403)
