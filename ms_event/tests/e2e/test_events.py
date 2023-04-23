import json

from django.test import TestCase

import app.models as models


class TestEventsManagement():
    def setUp(self) -> None:
        user = models.User.objects.create(
            username="test_user@gmail.com",
            email="test_user@gmail.com",
            first_name="Test",
            last_name="User",
        )
        models.ManuscriptUser.objects.create(user=user)
        return super().setUp()

    def test_create_event(self):
        body = {
            'name': 'Test Event',
            'image': 'image.png',
            'location': 'Almaty, Kazakhstan',
            'location_url': 'https://google.com',
            'description': 'Test Description',
            'full_description': 'Test Full Description',
            'start_date': '2021-01-01',
            'end_date': '2021-01-01',
            'author': 1,
            'tags': ['google', 'test'],
        }
        response = self.client.post(
            '/create/', body, content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(models.Event.objects.count(), 1)
        created_event = models.Event.objects.first()
        self.assertEqual(json.loads(response.content),
                         {"id": created_event.id})
