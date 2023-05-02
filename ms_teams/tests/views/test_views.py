import json
from django.test import TransactionTestCase, override_settings
from rest_framework.test import APIClient as Client
from django.core.files.uploadedfile import SimpleUploadedFile

import service_layer.unit_of_work as uow
import core.exceptions as exceptions
import core.constants as constants
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


def create_event(name="test_event", location='Almaty', tags=['test_tag1', 'test_tag2'], is_active=True):
    django_uow = uow.DjangoORMUnitOfWork()
    with django_uow:
        data = {
            "name": name,
            "is_active": is_active
        }
        event = django_uow.event.create(**data)
        return event


def create_team(user, event, name='test_team',  is_active=True):
    django_uow = uow.DjangoORMUnitOfWork()
    with django_uow:
        team = django_uow.team.create(
            name=name, event=event, is_active=is_active)
        team.save()
        django_uow.participant.create(
            user=user, team=team, role=constants.LEADER_ROLE, status=constants.APPLIED_STATUS)
        return team


def create_participation(user, team, role=constants.MEMBER_ROLE, status=constants.PENDING_STATUS):
    django_uow = uow.DjangoORMUnitOfWork()
    with django_uow:
        participation = django_uow.participant.create(
            user=user, team=team, role=role, status=status)
        return participation


@override_settings(MEDIA_ROOT=(TEST_DIR + '/media'), DEBUG=True)
class TestTeamManagement(TransactionTestCase):
    reset_sequences = True

    def setUp(self) -> None:
        self.client = Client()
        self.user = create_user()
        self.event = create_event()

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
        self.assertEqual(response.status_code, 400)
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
        self.assertEqual(response.status_code, 400)
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
        self.assertEqual(
            content['error'], None)

    def test_teams_get_should_return_filtered_teams(self):
        event_teams = []
        for _ in range(5):
            team = create_team(user=self.user, event=self.event)
            event_teams.append(team.to_dict())
        another_event = create_event(name='another_event')
        for _ in range(5):
            create_team(user=self.user, event=another_event)
        response = self.client.get(
            f"/teams/?event__id={self.event.id}")
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
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
        self.assertEqual(response.status_code, 200)
        content = response.data
        self.assertEqual(content['data']['name'], 'test_team updated')
        self.assertEqual(content['data']['event'], self.event.to_dict())
        self.assertEqual(content['data']['is_active'], True)

    def test_team_put_should_return_error_when_team_is_not_found(self):
        body = {"name": "test_team updated", }
        token = self.user.generate_jwt_token()
        response = self.client.put(
            f"/teams/999", **{"HTTP_AUTHORIZATION": f"Bearer {token}"}, data=body)
        self.assertEqual(response.status_code, 400)
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
        self.assertEqual(response.status_code, 400)
        content = response.data
        self.assertEqual(
            content['error'], exceptions.USER_IS_NOT_TEAM_LEADER_EXCEPTION_MESSAGE)

    def test_team_put_should_return_error_when_data_is_invalid(self):
        team = create_team(user=self.user, event=self.event)
        body = {"name": "", }
        token = self.user.generate_jwt_token()
        response = self.client.put(
            f"/teams/{team.id}", **{"HTTP_AUTHORIZATION": f"Bearer {token}"}, data=body)
        self.assertEqual(response.status_code, 400)
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
        self.assertEqual(response.status_code, 200)
        content = response.data
        self.assertEqual(content['data']['name'], 'test_team')
        self.assertEqual(content['data']['event'], self.event.to_dict())
        self.assertEqual(content['data']['is_active'], False)

    def test_team_delete_should_return_error_when_team_is_not_found(self):
        token = self.user.generate_jwt_token()
        response = self.client.delete(
            f"/teams/999", **{"HTTP_AUTHORIZATION": f"Bearer {token}"})
        self.assertEqual(response.status_code, 400)
        content = response.data
        self.assertEqual(content['error'],
                         exceptions.TEAM_NOT_FOUND_EXCEPTION_MESSAGE)

    def test_team_delete_should_return_error_when_user_is_not_leader_of_team(self):
        team = create_team(user=self.user, event=self.event)
        another_user = create_user(username='another_user')
        token = another_user.generate_jwt_token()
        response = self.client.delete(
            f"/teams/{team.id}", **{"HTTP_AUTHORIZATION": f"Bearer {token}"})
        self.assertEqual(response.status_code, 400)
        content = response.data
        self.assertEqual(
            content['error'], exceptions.USER_IS_NOT_TEAM_LEADER_EXCEPTION_MESSAGE)

    def test_team_delete_should_return_error_when_user_is_anonymous(self):
        response = self.client.delete(
            f"/teams/999", **{"HTTP_AUTHORIZATION": f"Bearer "}, )
        self.assertEqual(response.status_code, 403)

    # Join
    def test_team_participants_post_should_return_new_participan(self):
        team = create_team(user=self.user, event=self.event)
        another_user = create_user(username='another_user')
        body = {
            "user": another_user.id,
        }
        token = another_user.generate_jwt_token()
        response = self.client.post(
            f"/teams/{team.id}/participants", **{"HTTP_AUTHORIZATION": f"Bearer {token}"}, data=body)
        self.assertEqual(response.status_code, 201)
        content = response.data
        self.assertEqual(content['data']['user'], another_user.to_dict())
        self.assertEqual(content['data']['team'], team.to_dict())
        self.assertEqual(content['data']['role'], constants.MEMBER_ROLE)
        self.assertEqual(content['data']['status'], constants.PENDING_STATUS)

    def test_team_participants_post_should_return_error_when_team_is_not_found(self):
        another_user = create_user(username='another_user')
        body = {
            "user": another_user.id,
        }
        token = another_user.generate_jwt_token()
        response = self.client.post(
            f"/teams/999/participants", **{"HTTP_AUTHORIZATION": f"Bearer {token}"}, data=body)
        self.assertEqual(response.status_code, 400)
        content = response.data
        self.assertEqual(content['error'],
                         exceptions.TEAM_NOT_FOUND_EXCEPTION_MESSAGE)

    def test_team_participants_post_should_return_error_when_user_already_has_participation(self):
        team = create_team(user=self.user, event=self.event)
        create_participation(user=self.user, team=team)
        body = {
            "user": self.user.id,
        }
        token = self.user.generate_jwt_token()
        response = self.client.post(
            f"/teams/{team.id}/participants", **{"HTTP_AUTHORIZATION": f"Bearer {token}"}, data=body)
        self.assertEqual(response.status_code, 400)
        content = response.data
        self.assertEqual(
            content['error'], exceptions.USER_ALREADY_HAS_PARTICIPATION_EXCEPTION_MESSAGE)

    def test_team_participants_post_should_return_error_when_user_is_anonymous(self):
        team = create_team(user=self.user, event=self.event)
        another_user = create_user(username='another_user')
        body = {
            "user": another_user.id,
        }
        response = self.client.post(
            f"/teams/{team.id}/participants", **{"HTTP_AUTHORIZATION": f"Bearer "}, data=body)
        self.assertEqual(response.status_code, 403)

    # Leave
    def test_team_participants_delete_should_return_participant(self):
        team = create_team(user=self.user, event=self.event)
        another_user = create_user(username='another_user')
        create_participation(user=another_user, team=team,
                             status=constants.APPLIED_STATUS)
        token = another_user.generate_jwt_token()
        response = self.client.delete(
            f"/teams/{team.id}/participants", **{"HTTP_AUTHORIZATION": f"Bearer {token}"})
        self.assertEqual(response.status_code, 200)
        content = response.data
        self.assertEqual(content['data']['user'], another_user.to_dict())
        self.assertEqual(content['data']['team'], team.to_dict())
        self.assertEqual(content['data']['role'], constants.MEMBER_ROLE)
        self.assertEqual(content['data']['status'], constants.LEFT_STATUS)

    def test_team_participants_delete_should_return_error_when_team_is_not_found(self):
        team = create_team(user=self.user, event=self.event)
        another_user = create_user(username='another_user')
        participation = create_participation(
            user=another_user, team=team, status=constants.APPLIED_STATUS)
        token = self.user.generate_jwt_token()
        response = self.client.delete(
            f"/teams/999/participants", **{"HTTP_AUTHORIZATION": f"Bearer {token}"}, )
        self.assertEqual(response.status_code, 400)
        content = response.data
        self.assertEqual(content['error'],
                         exceptions.TEAM_NOT_FOUND_EXCEPTION_MESSAGE)

    def test_team_participants_delete_should_return_error_when_participant_is_not_found(self):
        team = create_team(user=self.user, event=self.event)
        another_user = create_user(username='another_user')
        token = another_user.generate_jwt_token()
        response = self.client.delete(
            f"/teams/{team.id}/participants", **{"HTTP_AUTHORIZATION": f"Bearer {token}"})
        self.assertEqual(response.status_code, 400)
        content = response.data
        self.assertEqual(
            content['error'], exceptions.PARTICIPANT_NOT_FOUND_EXCEPTION_MESSAGE)

    def test_team_participants_delete_should_return_error_when_user_is_anonymous(self):
        team = create_team(user=self.user, event=self.event)
        response = self.client.delete(
            f"/teams/{team.id}/participants")
        self.assertEqual(response.status_code, 403)

    # Apply/Decline

    def test_team_participant_put_should_return_participant_with_corresponding_status(self):
        team = create_team(user=self.user, event=self.event)
        another_user = create_user(username='another_user')
        participation = create_participation(user=another_user, team=team)
        body = {
            "status": constants.APPLIED_STATUS,
        }
        token = self.user.generate_jwt_token()
        response = self.client.put(
            f"/teams/{team.id}/participants/{participation.id}", **{"HTTP_AUTHORIZATION": f"Bearer {token}"}, data=body)
        self.assertEqual(response.status_code, 200)
        content = response.data
        self.assertEqual(content['data']['user'], another_user.to_dict())
        self.assertEqual(content['data']['team'], team.to_dict())
        self.assertEqual(content['data']['role'], constants.MEMBER_ROLE)
        self.assertEqual(content['data']['status'], constants.APPLIED_STATUS)
        another_user = create_user(username='another_user 2')
        participation = create_participation(user=another_user, team=team)
        body = {
            "status": constants.DECLINED_STATUS,
        }
        token = self.user.generate_jwt_token()
        response = self.client.put(
            f"/teams/{team.id}/participants/{participation.id}", **{"HTTP_AUTHORIZATION": f"Bearer {token}"}, data=body)
        self.assertEqual(response.status_code, 200)
        content = response.data
        self.assertEqual(content['data']['user'], another_user.to_dict())
        self.assertEqual(content['data']['team'], team.to_dict())
        self.assertEqual(content['data']['role'], constants.MEMBER_ROLE)
        self.assertEqual(content['data']['status'], constants.DECLINED_STATUS)

    def test_team_participant_put_should_return_error_when_team_is_not_found(self):
        team = create_team(user=self.user, event=self.event)
        another_user = create_user(username='another_user')
        participation = create_participation(user=another_user, team=team)
        body = {
            "status": constants.APPLIED_STATUS,
        }
        token = self.user.generate_jwt_token()
        response = self.client.put(
            f"/teams/999/participants/{participation.id}", **{"HTTP_AUTHORIZATION": f"Bearer {token}"}, data=body)
        self.assertEqual(response.status_code, 400)
        content = response.data
        self.assertEqual(content['error'],
                         exceptions.TEAM_NOT_FOUND_EXCEPTION_MESSAGE)

    def test_team_participant_put_should_return_error_when_participant_is_not_found(self):
        team = create_team(user=self.user, event=self.event)
        another_user = create_user(username='another_user')
        create_participation(user=another_user, team=team)
        body = {
            "status": constants.APPLIED_STATUS,
        }
        token = self.user.generate_jwt_token()
        response = self.client.put(
            f"/teams/{team.id}/participants/999", **{"HTTP_AUTHORIZATION": f"Bearer {token}"}, data=body)
        self.assertEqual(response.status_code, 400)
        content = response.data
        self.assertEqual(
            content['error'], exceptions.PARTICIPANT_NOT_FOUND_EXCEPTION_MESSAGE)

    def test_team_participant_put_should_return_error_when_user_is_not_team_leader(self):
        team = create_team(user=self.user, event=self.event)
        another_user = create_user(username='another_user')
        participation = create_participation(user=another_user, team=team)
        body = {
            "status": constants.APPLIED_STATUS,
        }
        token = another_user.generate_jwt_token()
        response = self.client.put(
            f"/teams/{team.id}/participants/{participation.id}", **{"HTTP_AUTHORIZATION": f"Bearer {token}"}, data=body)
        self.assertEqual(response.status_code, 400)
        content = response.data
        self.assertEqual(content['error'],
                         exceptions.USER_IS_NOT_TEAM_LEADER_EXCEPTION_MESSAGE)

    def test_team_participant_put_should_return_error_when_status_is_invalid(self):
        team = create_team(user=self.user, event=self.event)
        another_user = create_user(username='another_user')
        participation = create_participation(user=another_user, team=team)
        body = {
            "status": 'invalid_status',
        }
        token = self.user.generate_jwt_token()
        response = self.client.put(
            f"/teams/{team.id}/participants/{participation.id}", **{"HTTP_AUTHORIZATION": f"Bearer {token}"}, data=body)
        self.assertEqual(response.status_code, 400)
        content = response.data
        self.assertEqual(content['error'],
                         exceptions.INVALID_PARTICIPANT_STATUS_EXCEPTION_MESSAGE)

    def test_team_participant_put_should_return_error_when_status_is_already_set(self):
        team = create_team(user=self.user, event=self.event)
        another_user = create_user(username='another_user')
        participation = create_participation(
            user=another_user, team=team, status=constants.APPLIED_STATUS)
        body = {
            "status": constants.APPLIED_STATUS,
        }
        token = self.user.generate_jwt_token()
        response = self.client.put(
            f"/teams/{team.id}/participants/{participation.id}", **{"HTTP_AUTHORIZATION": f"Bearer {token}"}, data=body)
        self.assertEqual(response.status_code, 400)
        content = response.data
        self.assertEqual(content['error'],
                         exceptions.PARTICIPANT_ALREADY_HAS_STATUS_EXCEPTION_MESSAGE)

    def test_team_participant_put_should_return_error_when_user_is_anonymous(self):
        team = create_team(user=self.user, event=self.event)
        another_user = create_user(username='another_user')
        participation = create_participation(user=another_user, team=team)
        body = {
            "status": constants.APPLIED_STATUS,
        }
        response = self.client.put(
            f"/teams/{team.id}/participants/{participation.id}", data=body)
        self.assertEqual(response.status_code, 403)

    # Kick
    def test_team_participant_put_should_return_participant_with_kicked_status(self):
        team = create_team(user=self.user, event=self.event)
        another_user = create_user(username='another_user')
        participation = create_participation(
            user=another_user, team=team, status=constants.APPLIED_STATUS)
        token = self.user.generate_jwt_token()
        response = self.client.delete(
            f"/teams/{team.id}/participants/{participation.id}", **{"HTTP_AUTHORIZATION": f"Bearer {token}"})
        self.assertEqual(response.status_code, 200)
        content = response.data
        self.assertEqual(content['data']['user'], another_user.to_dict())
        self.assertEqual(content['data']['team'], team.to_dict())
        self.assertEqual(content['data']['role'], constants.MEMBER_ROLE)
        self.assertEqual(content['data']['status'], constants.KICKED_STATUS)

    def test_team_participant_put_should_return_error_when_team_is_not_found(self):
        team = create_team(user=self.user, event=self.event)
        another_user = create_user(username='another_user')
        participation = create_participation(
            user=another_user, team=team, status=constants.APPLIED_STATUS)
        token = self.user.generate_jwt_token()
        response = self.client.delete(
            f"/teams/999/participants/{participation.id}", **{"HTTP_AUTHORIZATION": f"Bearer {token}"}, )
        self.assertEqual(response.status_code, 400)
        content = response.data
        self.assertEqual(content['error'],
                         exceptions.TEAM_NOT_FOUND_EXCEPTION_MESSAGE)

    def test_team_participant_put_should_return_error_when_participant_is_not_found(self):
        team = create_team(user=self.user, event=self.event)
        another_user = create_user(username='another_user')
        create_participation(user=another_user, team=team,
                             status=constants.APPLIED_STATUS)
        token = self.user.generate_jwt_token()
        response = self.client.delete(
            f"/teams/{team.id}/participants/999", **{"HTTP_AUTHORIZATION": f"Bearer {token}"})
        self.assertEqual(response.status_code, 400)
        content = response.data
        self.assertEqual(
            content['error'], exceptions.PARTICIPANT_NOT_FOUND_EXCEPTION_MESSAGE)

    def test_team_participant_put_should_return_error_when_user_is_not_team_leader(self):
        team = create_team(user=self.user, event=self.event)
        another_user = create_user(username='another_user')
        participation = create_participation(
            user=another_user, team=team, status=constants.APPLIED_STATUS)
        token = another_user.generate_jwt_token()
        response = self.client.delete(
            f"/teams/{team.id}/participants/{participation.id}", **{"HTTP_AUTHORIZATION": f"Bearer {token}"})
        self.assertEqual(response.status_code, 400)
        content = response.data
        self.assertEqual(content['error'],
                         exceptions.USER_IS_NOT_TEAM_LEADER_EXCEPTION_MESSAGE)

    def test_team_participant_put_should_return_error_when_user_is_anonymous(self):
        team = create_team(user=self.user, event=self.event)
        another_user = create_user(username='another_user')
        participation = create_participation(
            user=another_user, team=team, status=constants.APPLIED_STATUS)
        response = self.client.delete(
            f"/teams/{team.id}/participants/{participation.id}")
        self.assertEqual(response.status_code, 403)
