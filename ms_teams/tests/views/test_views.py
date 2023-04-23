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
        data = {
            "name": name,
            "is_active": is_active
        }
        event = django_uow.event.create(**data)
        return event


def create_team(user, event, name='test_team', members=[], is_active=True):
    django_uow = uow.DjangoORMUnitOfWork()
    with django_uow:
        team = django_uow.team.create(
            name=name, leader=user, event=event, is_active=is_active)
        team.members.set(members)
        team.save()
        return team


@override_settings(MEDIA_ROOT=(TEST_DIR + '/media'))
class TestTeamManagement(TransactionTestCase):
    reset_sequences = True

    def setUp(self) -> None:
        self.client = Client()
        self.user = create_user()
        self.event = create_event(user=self.user)

    def tearDown(self) -> None:
        try:
            shutil.rmtree(TEST_DIR)
        except OSError:
            pass

    # Create
    def test_teams_post_should_return_team_data(self):
        image = SimpleUploadedFile(
            "test_image.jpg", b"file_content", content_type="image/jpeg")
        body = {
            "name": "test_team",
            "image": image,
        }
        token = self.user.generate_jwt_token()
        response = self.client.post(
            f"/teams/?event_id={self.event.id}", data=body, **{"HTTP_AUTHORIZATION": f"Bearer {token}"})
        self.assertEqual(response.status_code, 201)
        content = json.loads(response.content)
        self.assertEqual(content['data']['name'], 'test_team')
        self.assertEqual(content['data']['leader'], self.user.to_dict())
        self.assertEqual(content['data']['members'], [])
        self.assertEqual(content['data']['event'], self.event.to_dict())
        self.assertEqual(content['data']['is_active'], True)

    def test_teams_post_should_return_error_when_data_is_invalid(self):
        image = SimpleUploadedFile(
            "test_image.jpg", b"file_content", content_type="image/jpeg")
        body = {
            "name": "",
            "image": image,
        }
        token = self.user.generate_jwt_token()
        response = self.client.post(
            f"/teams/", data=body, **{"HTTP_AUTHORIZATION": f"Bearer {token}"})
        self.assertEqual(response.status_code, 401)
        content = json.loads(response.content)
        self.assertEqual(
            content['error'], exceptions.INVALID_TEAM_DATA_EXCEPTION_MESSAGE)

    def test_teams_post_should_return_error_when_user_is_anonymous(self):
        image = SimpleUploadedFile(
            "test_image.jpg", b"file_content", content_type="image/jpeg")
        body = {
            "name": "",
            "image": image,
        }
        response = self.client.post(
            f"/teams/", data=body, **{"HTTP_AUTHORIZATION": f"Bearer "})
        self.assertEqual(response.status_code, 403)

    def test_teams_post_should_return_error_when_event_is_not_found(self):
        image = SimpleUploadedFile(
            "test_image.jpg", b"file_content", content_type="image/jpeg")
        body = {
            "name": "test_event",
            "image": image,
        }
        token = self.user.generate_jwt_token()
        response = self.client.post(
            f"/teams/", data=body, **{"HTTP_AUTHORIZATION": f"Bearer {token}"})
        self.assertEqual(response.status_code, 401)
        content = json.loads(response.content)
        self.assertEqual(
            content['error'], exceptions.EVENT_NOT_FOUND_EXCEPTION_MESSAGE)

    # Get

    def test_team_get_should_return_team_data(self):
        team = create_team(user=self.user, event=self.event)
        response = self.client.get(
            f"/teams/{team.id}")
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content['data'], team.to_dict())
        self.assertEqual(content['error'], None)

    def test_team_get_should_return_error_when_team_is_not_found(self):
        response = self.client.get(
            f"/teams/999")
        self.assertEqual(response.status_code, 404)
        content = json.loads(response.content)
        self.assertEqual(content['data'], None)
        self.assertEqual(
            content['error'], exceptions.TEAM_NOT_FOUND_EXCEPTION_MESSAGE)

    # List

    def test_teams_get_should_return_teams(self):
        active_teams = []
        for _ in range(5):
            team = create_team(user=self.user, event=self.event)
            active_teams.append(team.to_dict())
        for _ in range(5):
            create_team(user=self.user, event=self.event, is_active=False)
        response = self.client.get(
            f"/teams/")
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertListEqual(
            content['data'], active_teams)
        self.assertEqual(
            content['error'], None)

    def test_teams_get_should_return_filtered_teams(self):
        event_teams = []
        for _ in range(5):
            team = create_team(user=self.user, event=self.event)
            event_teams.append(team.to_dict())
        another_event = create_event(user=self.user, name='another_event')
        for _ in range(5):
            create_team(user=self.user, event=another_event)
        response = self.client.get(
            f"/teams/?event__id={self.event.id}")
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertListEqual(
            content['data'], event_teams)
        self.assertEqual(
            content['error'], None)

    # Edit
    def test_team_put_should_edit_team_and_return_team_data(self):
        team = create_team(user=self.user, event=self.event)
        body = {
            "name": "test_team updated",
        }
        token = self.user.generate_jwt_token()
        response = self.client.put(
            f"/teams/{team.id}", **{"HTTP_AUTHORIZATION": f"Bearer {token}"}, data=body)
        self.assertEqual(response.status_code, 204)
        content = response.data
        self.assertEqual(content['data']['name'], 'test_team updated')
        self.assertEqual(content['data']['leader'], self.user.to_dict())
        self.assertEqual(content['data']['members'], [])
        self.assertEqual(content['data']['event'], self.event.to_dict())
        self.assertEqual(content['data']['is_active'], True)

    def test_team_put_should_return_error_when_team_is_not_found(self):
        body = {"name": "test_team updated", }
        token = self.user.generate_jwt_token()
        response = self.client.put(
            f"/teams/999", **{"HTTP_AUTHORIZATION": f"Bearer {token}"}, data=body)
        self.assertEqual(response.status_code, 401)
        content = response.data
        self.assertEqual(
            content['error'], exceptions.TEAM_NOT_FOUND_EXCEPTION_MESSAGE)

    def test_team_put_should_return_error_when_user_is_not_leader_of_team(self):
        team = create_team(user=self.user, event=self.event)
        body = {"name": "test_team updated", }
        another_user = create_user(username='another_user')
        token = another_user.generate_jwt_token()
        response = self.client.put(
            f"/teams/{team.id}", **{"HTTP_AUTHORIZATION": f"Bearer {token}"}, data=body)
        self.assertEqual(response.status_code, 401)
        content = response.data
        self.assertEqual(
            content['error'], exceptions.USER_IS_NOT_TEAM_LEADER_EXCEPTION_MESSAGE)

    def test_team_put_should_return_error_when_data_is_invalid(self):
        team = create_team(user=self.user, event=self.event)
        body = {"name": "", }
        token = self.user.generate_jwt_token()
        response = self.client.put(
            f"/teams/{team.id}", **{"HTTP_AUTHORIZATION": f"Bearer {token}"}, data=body)
        self.assertEqual(response.status_code, 401)
        content = response.data
        self.assertEqual(
            content['error'], exceptions.INVALID_TEAM_DATA_EXCEPTION_MESSAGE)

    def test_team_put_should_return_error_when_user_is_anonymous(self):
        body = {"name": "", }
        response = self.client.put(
            f"/teams/999", **{"HTTP_AUTHORIZATION": f"Bearer "}, data=body)
        self.assertEqual(response.status_code, 403)

    # Deactivate
    def test_team_delete_should_return_team(self):
        team = create_team(user=self.user, event=self.event)
        token = self.user.generate_jwt_token()
        response = self.client.delete(
            f"/teams/{team.id}", **{"HTTP_AUTHORIZATION": f"Bearer {token}"})
        self.assertEqual(response.status_code, 204)
        content = response.data
        self.assertEqual(content['data']['name'], 'test_team')
        self.assertEqual(content['data']['leader'], self.user.to_dict())
        self.assertEqual(content['data']['members'], [])
        self.assertEqual(content['data']['event'], self.event.to_dict())
        self.assertEqual(content['data']['is_active'], False)

    def test_team_delete_should_return_error_when_team_is_not_found(self):
        token = self.user.generate_jwt_token()
        response = self.client.delete(
            f"/teams/999", **{"HTTP_AUTHORIZATION": f"Bearer {token}"})
        self.assertEqual(response.status_code, 401)
        content = response.data
        self.assertEqual(content['error'],
                         exceptions.TEAM_NOT_FOUND_EXCEPTION_MESSAGE)

    def test_team_delete_should_return_error_when_user_is_not_leader_of_team(self):
        team = create_team(user=self.user, event=self.event)
        another_user = create_user(username='another_user')
        token = another_user.generate_jwt_token()
        response = self.client.delete(
            f"/teams/{team.id}", **{"HTTP_AUTHORIZATION": f"Bearer {token}"})
        self.assertEqual(response.status_code, 401)
        content = response.data
        self.assertEqual(
            content['error'], exceptions.USER_IS_NOT_TEAM_LEADER_EXCEPTION_MESSAGE)

    def test_team_delete_should_return_error_when_user_is_anonymous(self):
        response = self.client.delete(
            f"/teams/999", **{"HTTP_AUTHORIZATION": f"Bearer "}, )
        self.assertEqual(response.status_code, 403)

    # Kick
    def test_kick_team_member_should_return_team_data(self):
        user_1 = create_user(username='user_1')
        user_2 = create_user(username='user_2')
        user_to_kick = create_user(username='user_to_kick')
        team = create_team(user=self.user, event=self.event,
                           members=[user_1, user_2, user_to_kick])
        token = self.user.generate_jwt_token()
        response = self.client.get(
            f"/teams/{team.id}/kick/{user_to_kick.id}", **{"HTTP_AUTHORIZATION": f"Bearer {token}"})
        self.assertEqual(response.status_code, 200)
        content = response.data
        self.assertEqual(content['data']['name'], 'test_team')
        self.assertEqual(content['data']['leader'], self.user.to_dict())
        self.assertEqual(content['data']['members'], [
                         user_1.to_dict(), user_2.to_dict()])
        self.assertEqual(content['data']['event'], self.event.to_dict())
        self.assertEqual(content['data']['is_active'], True)

    def test_kick_team_member_should_return_error_when_team_is_not_found(self):
        user_to_kick = create_user(username='user_to_kick')
        token = self.user.generate_jwt_token()
        response = self.client.get(
            f"/teams/999/kick/{user_to_kick.id}", **{"HTTP_AUTHORIZATION": f"Bearer {token}"})
        self.assertEqual(response.status_code, 401)
        content = response.data
        self.assertEqual(content['error'],
                         exceptions.TEAM_NOT_FOUND_EXCEPTION_MESSAGE)

    def test_kick_team_member_should_return_error_when_user_is_not_leader_of_team(self):
        team = create_team(user=self.user, event=self.event)
        user_to_kick = create_user(username='user_to_kick')
        another_user = create_user(username='another_user')
        token = another_user.generate_jwt_token()
        response = self.client.get(
            f"/teams/{team.id}/kick/{user_to_kick.id}", **{"HTTP_AUTHORIZATION": f"Bearer {token}"})
        self.assertEqual(response.status_code, 401)
        content = response.data
        self.assertEqual(content['error'],
                         exceptions.USER_IS_NOT_TEAM_LEADER_EXCEPTION_MESSAGE)

    def test_kick_team_member_should_return_error_when_user_is_anonymous(self):
        user_to_kick = create_user(username='user_to_kick')
        response = self.client.get(
            f"/teams/999/kick/{user_to_kick.id}", **{"HTTP_AUTHORIZATION": f"Bearer "})
        self.assertEqual(response.status_code, 403)
