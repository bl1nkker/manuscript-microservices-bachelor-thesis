from django.test import TestCase

import app.models as models


class TestUser(TestCase):

    def setUp(self) -> None:
        self.user = models.User.objects.create(
            username="test_user@gmail.com",
            email="test_user@gmail.com",
            first_name="Test",
            last_name="User",
        )

        return super().setUp()

    def test_to_dict_should_return_dict(self):
        m_user = models.ManuscriptUser.objects.create(
            user=self.user
        )
        user_dict = m_user.to_dict()
        self.assertEqual(type(user_dict), dict)
        self.assertEqual(user_dict[
                         'username'], 'test_user@gmail.com')
        self.assertEqual(user_dict['email'], 'test_user@gmail.com')
        self.assertEqual(user_dict['first_name'], 'Test')
        self.assertEqual(user_dict['last_name'], 'User')
        self.assertEqual(user_dict['id'], m_user.id)
