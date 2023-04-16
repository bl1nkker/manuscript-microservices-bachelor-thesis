from django.test import TestCase

import app.models as models


class TestEvent(TestCase):

    def setUp(self) -> None:
        user = models.User.objects.create(
            username="test_user@gmail.com",
            email="test_user@gmail.com",
            first_name="Test",
            last_name="User",
        )
        self.author = models.ManuscriptUser.objects.create(
            user=user
        )

    def test_to_dict_should_return_dict(self):
        event = models.Event.objects.create(
            name="Test Event",
            location="Almaty, Kazakhstan",
            location_url="https://google.com",
            description="Test Description",
            full_description="Test Full Description",
            start_date="2021-01-01",
            end_date="2021-01-02",
            author=self.author,
            tags="[]",
        )
        event_dict = event.to_dict()
        self.assertEqual(models.Event.objects.count(), 1)
        self.assertEqual(type(event_dict), dict)
        self.assertEqual(event_dict['name'], 'Test Event')
        self.assertEqual(event_dict['location'], 'Almaty, Kazakhstan')
        self.assertEqual(event_dict['location_url'], 'https://google.com')
        self.assertEqual(event_dict['description'], 'Test Description')
        self.assertEqual(
            event_dict['full_description'], 'Test Full Description')
        self.assertEqual(event_dict['start_date'], '2021-01-01')
        self.assertEqual(event_dict['end_date'], '2021-01-02')
        self.assertEqual(event_dict['tags'], '[]')
        self.assertEqual(event_dict['id'], event.id)
        self.assertEqual(event_dict['author'], event.author.to_dict())
