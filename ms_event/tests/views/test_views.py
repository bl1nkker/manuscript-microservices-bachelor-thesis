import json
from django.test import TransactionTestCase, override_settings
from rest_framework.test import APIClient as Client
from django.core.files.uploadedfile import SimpleUploadedFile


import service_layer.unit_of_work as uow
import core.exceptions as exceptions

import shutil

TEST_DIR = 'test_data'


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


def create_event(user, name="test_event", location='Almaty', tags=['test_tag1', 'test_tag2'], is_active=True):
    django_uow = uow.DjangoORMUnitOfWork()
    with django_uow:
        image = SimpleUploadedFile(
            "test_image.jpg", b"file_content", content_type="image/jpeg")
        data = {
            "name": name,
            "image": image,
            "location": location,
            "location_url": 'https://www.google.com',
            "description": 'Test description',
            "full_description": 'Test full description',
            "start_date": '2020-01-01',
            "end_date": '2020-01-02',
            "author": user,
            "tags": tags,
            "is_active": is_active
        }
        event = django_uow.event.create(**data)
        return event


@override_settings(MEDIA_ROOT=(TEST_DIR + '/media'), DEBUG=True)
class TestEventManagement(TransactionTestCase):
    reset_sequences = True

    def setUp(self) -> None:
        self.client = Client()
        self.user = create_user()
        self.token = self.user.generate_jwt_token()
        self.event = create_event(user=self.user)

    def tearDown(self) -> None:

        try:
            shutil.rmtree(TEST_DIR)
        except OSError:
            pass
    # Get event

    def test_get_event_should_return_event_data(self):
        response = self.client.get(
            f"/events/{self.event.id}")
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content['data'], self.event.to_dict())
        self.assertEqual(content['error'], None)

    def test_get_event_should_return_error_when_event_does_not_exists(self):
        response = self.client.get(
            f"/events/999")
        self.assertEqual(response.status_code, 404)
        content = json.loads(response.content)
        self.assertEqual(content['data'], None)
        self.assertEqual(
            content['error'], exceptions.EVENT_NOT_FOUND_EXCEPTION_MESSAGE)

        # Get list of events

    def test_events_get_should_return_list_of_events_by_location(self):
        city2_events = []
        city1_events = []
        for _ in range(5):
            event = create_event(user=self.user, location='Astana')
            city1_events.append(event.to_dict())
        for _ in range(5):
            event = create_event(user=self.user, location='Qostanay')
            city2_events.append(event.to_dict())
        response = self.client.get(
            f"/events/?location=Qostanay")
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertListEqual(content['data'], city2_events)
        self.assertEqual(
            content['error'], None)
        response = self.client.get(
            f"/events/?location=Astana")
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertListEqual(content['data'], city1_events)
        self.assertEqual(
            content['error'], None)

    def test_events_get_should_return_list_of_events_by_tags(self):
        tag2_events = []
        tag1_events = []
        for _ in range(5):
            event = create_event(user=self.user, tags=['tag1', 'tag3'])
            tag1_events.append(event.to_dict())
        for _ in range(5):
            event = create_event(user=self.user, tags=['tag2', 'tag3'])
            tag2_events.append(event.to_dict())
        response = self.client.get(
            f"/events/?tags__contains=tag1")
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertListEqual(content['data'], tag1_events)
        self.assertEqual(
            content['error'], None)
        response = self.client.get(
            f"/events/?tags__contains=tag2")
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertListEqual(content['data'], tag2_events)
        self.assertEqual(
            content['error'], None)
        response = self.client.get(
            f"/events/?tags__contains=tag3")
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertListEqual(content['data'], [*tag1_events, *tag2_events])
        self.assertEqual(
            content['error'], None)

    def test_events_get_should_return_list_of_active_events_when_no_params_passed(self):
        active_events = [self.event.to_dict()]
        for _ in range(5):
            event = create_event(user=self.user, is_active=True)
            active_events.append(event.to_dict())
        for _ in range(5):
            create_event(user=self.user, is_active=False)

        response = self.client.get(
            f"/events/")
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertListEqual(
            content['data'], active_events)
        self.assertEqual(
            content['error'], None)

    def test_events_get_should_return_list_of_user_events_by_user(self):
        user_events = [self.event.to_dict()]
        another_user = create_user(username='another@gmail.com')
        for _ in range(5):
            create_event(user=another_user)
        for _ in range(5):
            event = create_event(user=self.user, tags=['tag2', 'tag3'])
            user_events.append(event.to_dict())
        response = self.client.get(
            f"/events/?author__id={self.user.id}")
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)

        self.assertListEqual(content['data'], user_events)
        self.assertEqual(
            content['error'], None)

    # Create event
    def test_events_post_should_return_event(self):
        image = SimpleUploadedFile(
            "test_image.jpg", b"file_content", content_type="image/jpeg")
        body = {
            "name": "test_event",
            "image": image,
            "location": 'Almaty',
            "location_url": 'https://www.google.com',
            "description": 'Test description',
            "full_description": 'Test full description',
            "start_date": '2020-01-01',
            "end_date": '2020-01-02',
            "tags": ['test_tag1', 'test_tag2'],
        }
        token = self.user.generate_jwt_token()
        response = self.client.post(
            f"/events/", data=body, **{"HTTP_AUTHORIZATION": f"Bearer {token}"})
        self.assertEqual(response.status_code, 201)
        content = json.loads(response.content)
        self.assertEqual(content['data']['name'], 'test_event')
        self.assertEqual(content['data']["location"], 'Almaty')
        self.assertEqual(content['data']["location_url"],
                         'https://www.google.com')
        self.assertEqual(content['data']["description"], 'Test description')
        self.assertEqual(
            content['data']["full_description"], 'Test full description')
        self.assertEqual(content['data']["start_date"], '2020-01-01')
        self.assertEqual(content['data']["end_date"], '2020-01-02')
        self.assertEqual(content['data']["tags"], ['test_tag1', 'test_tag2'])
        self.assertEqual(content['data']["author"], self.user.to_dict())

    def test_events_post_should_return_error_when_data_is_invalid(self):
        image = SimpleUploadedFile(
            "test_image.jpg", b"file_content", content_type="image/jpeg")
        body = {
            "name": "",
            "image": image,
            "location": 'Almaty',
            "location_url": 'https://www.google.com',
            "description": 'Test description',
            "full_description": 'Test full description',
            "start_date": '2020-01-01',
            "end_date": '2020-01-02',
            "tags": ['test_tag1', 'test_tag2'],
        }
        token = self.user.generate_jwt_token()
        response = self.client.post(
            f"/events/", data=body, **{"HTTP_AUTHORIZATION": f"Bearer {token}"})
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(
            content['error'], exceptions.INVALID_EVENT_DATA_EXCEPTION_MESSAGE)

    def test_events_post_should_return_error_when_user_is_anonymous(self):
        image = SimpleUploadedFile(
            "test_image.jpg", b"file_content", content_type="image/jpeg")
        body = {
            "name": "hello_world",
            "image": image,
            "location": 'Almaty',
            "location_url": 'https://www.google.com',
            "description": 'Test description',
            "full_description": 'Test full description',
            "start_date": '2020-01-01',
            "end_date": '2020-01-02',
            "tags": ['test_tag1', 'test_tag2'],
        }
        response = self.client.post(
            f"/events/", data=body)
        self.assertEqual(response.status_code, 403)

    # Edit event
    def test_event_put_should_return_event(self):
        body = {
            "name": "test_event updated",
            "image": 'test_image',
            "location": 'Almaty, updated',
            "location_url": 'https://www.google.com',
            "description": 'Test description',
            "full_description": 'Test full description',
            "start_date": '2020-11-01',
            "end_date": '2020-11-02',
        }
        token = self.user.generate_jwt_token()
        response = self.client.put(
            f"/events/{self.event.id}", **{"HTTP_AUTHORIZATION": f"Bearer {token}"}, data=body,)
        self.assertEqual(response.status_code, 204)
        content = response.data
        self.assertEqual(content['data']['name'], 'test_event updated')
        self.assertEqual(content['data']["location"], 'Almaty, updated')
        self.assertEqual(content['data']["location_url"],
                         'https://www.google.com')
        self.assertEqual(content['data']["description"], 'Test description')
        self.assertEqual(
            content['data']["full_description"], 'Test full description')
        self.assertEqual(content['data']["start_date"], '2020-11-01')
        self.assertEqual(content['data']["end_date"], '2020-11-02')
        self.assertEqual(content['data']["tags"], ['test_tag1', 'test_tag2'])
        self.assertEqual(content['data']["author"], self.user.to_dict())

    def test_event_put_should_return_error_when_data_is_invalid(self):
        body = {
            "name": "",
            "image": 'test_image',
            "location": 'Almaty, updated',
            "location_url": 'https://www.google.com',
            "description": 'Test description',
            "full_description": 'Test full description',
            "start_date": '2020-11-01',
            "end_date": '2020-11-02',
        }
        token = self.user.generate_jwt_token()
        response = self.client.put(
            f"/events/{self.event.id}", data=body, **{"HTTP_AUTHORIZATION": f"Bearer {token}"})
        self.assertEqual(response.status_code, 400)
        content = response.data
        self.assertEqual(
            content['error'], exceptions.INVALID_EVENT_DATA_EXCEPTION_MESSAGE)

    def test_event_put_should_return_error_when_event_is_not_found(self):
        body = {
            "name": "test_event updated",
            "image": 'test_image',
            "location": 'Almaty, updated',
            "location_url": 'https://www.google.com',
            "description": 'Test description',
            "full_description": 'Test full description',
            "start_date": '2020-11-01',
            "end_date": '2020-11-02',
        }
        token = self.user.generate_jwt_token()
        response = self.client.put(
            f"/events/999", data=body, **{"HTTP_AUTHORIZATION": f"Bearer {token}"})
        self.assertEqual(response.status_code, 400)
        content = response.data
        self.assertEqual(
            content['error'], exceptions.EVENT_NOT_FOUND_EXCEPTION_MESSAGE)

    def test_event_put_should_return_error_when_user_is_not_author(self):
        body = {
            "name": "test_event updated",
            "image": 'test_image',
            "location": 'Almaty, updated',
            "location_url": 'https://www.google.com',
            "description": 'Test description',
            "full_description": 'Test full description',
            "start_date": '2020-11-01',
            "end_date": '2020-11-02',
        }
        another_user = create_user(username='test_user2')
        token = another_user.generate_jwt_token()
        response = self.client.put(
            f"/events/{self.event.id}", data=body, **{"HTTP_AUTHORIZATION": f"Bearer {token}"})
        self.assertEqual(response.status_code, 400)
        content = response.data
        self.assertEqual(
            content['error'], exceptions.USER_IS_NOT_EVENT_AUTHOR_EXCEPTION_MESSAGE)

    def test_event_put_should_return_error_when_user_is_anonymous(self):
        body = {
            "name": "test_event updated",
            "image": 'test_image',
            "location": 'Almaty, updated',
            "location_url": 'https://www.google.com',
            "description": 'Test description',
            "full_description": 'Test full description',
            "start_date": '2020-11-01',
            "end_date": '2020-11-02',
        }
        response = self.client.put(
            f"/events/{self.event.id}", data=body)
        self.assertEqual(response.status_code, 403)

    def test_event_delete_should_deactivate_event(self):
        token = self.user.generate_jwt_token()
        response = self.client.delete(
            f"/events/{self.event.id}", **{"HTTP_AUTHORIZATION": f"Bearer {token}"})
        self.assertEqual(response.status_code, 204)
        content = response.data
        self.assertEqual(content['data']['name'], 'test_event')
        self.assertEqual(content['data']["location"], 'Almaty')
        self.assertEqual(content['data']["location_url"],
                         'https://www.google.com')
        self.assertEqual(content['data']["description"], 'Test description')
        self.assertEqual(content['data']["is_active"], False)
        self.assertEqual(
            content['data']["full_description"], 'Test full description')
        self.assertEqual(content['data']["start_date"], '2020-01-01')
        self.assertEqual(content['data']["end_date"], '2020-01-02')
        self.assertEqual(content['data']["tags"], ['test_tag1', 'test_tag2'])
        self.assertEqual(content['data']["author"], self.user.to_dict())

    def test_event_delete_should_return_error_when_event_is_not_found(self):
        token = self.user.generate_jwt_token()
        response = self.client.delete(
            f"/events/999", **{"HTTP_AUTHORIZATION": f"Bearer {token}"})
        self.assertEqual(response.status_code, 400)
        content = response.data
        self.assertEqual(content['error'],
                         exceptions.EVENT_NOT_FOUND_EXCEPTION_MESSAGE)

    def test_event_delete_should_return_error_when_user_is_not_author(self):
        another_user = create_user(username='test_user2')
        token = another_user.generate_jwt_token()
        response = self.client.delete(
            f"/events/{self.event.id}", **{"HTTP_AUTHORIZATION": f"Bearer {token}"})
        self.assertEqual(response.status_code, 400)
        content = response.data
        self.assertEqual(content['error'],
                         exceptions.USER_IS_NOT_EVENT_AUTHOR_EXCEPTION_MESSAGE)

    def test_event_delete_should_return_error_when_user_is_anonymous(self):
        response = self.client.delete(
            f"/events/{self.event.id}")
        self.assertEqual(response.status_code, 403)
