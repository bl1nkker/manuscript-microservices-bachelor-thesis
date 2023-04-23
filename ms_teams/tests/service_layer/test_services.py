import json
import pika

from django.test import TestCase
from django.conf import settings

from service_layer.result import Result
import service_layer.services as services
import service_layer.unit_of_work as uow
import core.exceptions as exceptions
import service_layer.message_broker as mb


class TestTeamServices(TestCase):
    def setUp(self) -> None:
        self.uow = uow.FakeUnitOfWork()
        self.user = self.uow.user.create(username="test", password="test")
        self.event = self.uow.event.create(name="test_event")
        return super().setUp()

    def create_team(self, name='test_event', user=None, event=None, members=[]):
        if user is None:
            user = self.user
        if event is None:
            event = self.event
        return self.uow.team.create(name=name, leader=user, event=event, members=members)

    # Create
    def test_create_team_service_should_create_team_and_return_result_with_team(self):
        body = {
            "name": 'test_event',
            "image": 'test_image',
        }
        expected = Result(data={
            "id": 1,
            "name": "test_event",
            "image": 'test_image',
            "leader": self.user,
            "members": [],
            "event": self.event,
            "is_active": True,
        }, error=None)
        result = services.create_team_service(
            uow=self.uow, event_id=self.event.id, username=self.user.username, **body)
        self.assertEqual(expected, result)

    def test_create_team_service_should_return_result_with_error_when_data_is_invalid(self):
        body = {
            "name": '',
            "image": 'test_image',
        }
        expected = Result(data=None, error=exceptions.InvalidTeamDataException)
        result = services.create_team_service(
            uow=self.uow, event_id=self.event.id, username=self.user.username, **body)
        self.assertEqual(expected, result)

    # Get
    def test_get_team_service_should_return_result_with_team(self):
        team = self.create_team()
        expected = Result(data=team.to_dict(), error=None)
        result = services.get_team_service(uow=self.uow, team_id=team.id)
        self.assertEqual(expected, result)

    def test_get_team_service_should_return_result_with_error_when_team_is_not_found(self):
        expected = Result(data=None, error=exceptions.TeamNotFoundException)
        result = services.get_team_service(uow=self.uow, team_id=999)
        self.assertEqual(expected, result)

    # List
    def test_list_team_service_should_return_result_with_teams(self):
        for _ in range(10):
            self.create_team(name='new team')
        expected = Result(data=[team.to_dict()
                          for team in self.uow.team.list()], error=None)
        result = services.list_team_service(uow=self.uow)
        self.assertEqual(expected, result)

    def test_list_team_service_should_return_result_with_filtered_teams(self):
        another_event = self.uow.event.create(name="another_event")
        expected_events = []
        for _ in range(10):
            self.create_team(name='new team', event=another_event)
        for _ in range(3):
            event = self.create_team(name='new team')
            expected_events.append(event)
        expected = Result(data=[team.to_dict()
                          for team in expected_events], error=None)
        result = services.list_team_service(uow=self.uow, event=self.event)
        self.assertEqual(expected, result)

    # Edit
    def test_edit_team_service_should_edit_team_and_return_result_with_team(self):
        team = self.create_team()
        expected = Result(data={
            "id": 1,
            "name": "updated event",
            "image": 'updated image',
            "leader": self.user,
            "members": [],
            "event": self.event,
            "is_active": True,
        }, error=None)
        result = services.edit_team_service(
            uow=self.uow, username=self.user.username, team_id=team.id, name='updated event', image='updated image')
        self.assertEqual(expected, result)

    def test_edit_team_service_should_return_result_with_error_when_team_is_not_found(self):
        expected = Result(data=None, error=exceptions.TeamNotFoundException)
        result = services.edit_team_service(
            uow=self.uow, username=self.user.username, team_id=999, name='updated event', image='updated image')
        self.assertEqual(expected, result)

    def test_edit_team_service_should_return_result_with_error_when_user_is_not_leader_of_team(self):
        team = self.create_team()
        expected = Result(
            data=None, error=exceptions.UserIsNotTeamLeaderException)
        another_user = self.uow.user.create(username="another_user")
        result = services.edit_team_service(
            uow=self.uow, username=another_user.username, team_id=team.id, name='updated event', image='updated image')
        self.assertEqual(expected, result)

    def test_edit_team_service_should_return_result_with_error_when_data_is_invalid(self):
        team = self.create_team()
        expected = Result(data=None, error=exceptions.InvalidTeamDataException)
        result = services.edit_team_service(
            uow=self.uow, username=self.user.username, team_id=team.id, name='', image='updated image')
        self.assertEqual(expected, result)

    # Deactivate
    def test_deactivate_team_service_should_deactivate_team_and_return_result_with_team(self):
        team = self.create_team()
        expected = Result(data={
            "id": 1,
            "name": "test_event",
            "image": '',
            "leader": self.user,
            "members": [],
            "event": self.event,
            "is_active": False,
        }, error=None)
        result = services.deactivate_team_service(
            uow=self.uow, username=self.user.username, team_id=team.id)
        self.assertEqual(expected, result)

    def test_deactivate_team_service_should_return_result_with_error_when_team_is_not_found(self):
        expected = Result(data=None, error=exceptions.TeamNotFoundException)
        result = services.deactivate_team_service(
            uow=self.uow, username=self.user.username, team_id=999)
        self.assertEqual(expected, result)

    def test_deactivate_team_service_should_return_result_with_error_when_user_is_not_leader_of_team(self):
        team = self.create_team()
        expected = Result(
            data=None, error=exceptions.UserIsNotTeamLeaderException)
        result = services.deactivate_team_service(
            uow=self.uow, username='unknown_username', team_id=team.id)
        self.assertEqual(expected, result)

    # Kick
    def test_kick_team_member_team_should_kick_team_member_and_return_result_with_team_and_send_message_to_message_broker(self):
        user_1 = self.uow.user.create(username="user_1")
        user_2 = self.uow.user.create(username="user_2")
        user_to_kick = self.uow.user.create(username="user_to_kick")
        team = self.create_team(members=[user_1, user_2, user_to_kick])
        expected = Result(data={
            "id": 1,
            "name": "test_event",
            "image": '',
            "leader": self.user,
            "members": [user_1, user_2],
            "event": self.event,
            "is_active": True,
        }, error=None)
        result = services.kick_team_member_service(
            uow=self.uow, username=self.user.username, team_id=team.id, member_id=user_to_kick.id)
        self.assertEqual(expected, result)
        # Subscribe to the queue and start consuming messages
        credentials = pika.URLParameters(settings.RABBITMQ_CONNECTION_URL)
        message_broker = mb.RabbitMQ(
            credentials.host, credentials.port, credentials.credentials.username, credentials.credentials.password, exchange=settings.RABBITMQ_EXCHANGE_NAME)
        message_broker.connect()
        message = message_broker.consume_last_message(
            queue=settings.RABBITMQ_QUEUE)
        self.assertEqual(json.loads(message), {
                         "user": user_to_kick.id, "team": team.id})

    def test_kick_team_service_should_return_result_with_error_when_team_is_not_found(self):
        expected = Result(data=None, error=exceptions.TeamNotFoundException)
        result = services.kick_team_member_service(
            uow=self.uow, username=self.user.username, team_id=999, member_id=999)
        self.assertEqual(expected, result)

    def test_kick_team_service_should_return_result_with_error_when_user_is_not_leader_of_team(self):
        user_1 = self.uow.user.create(username="user_1")
        user_2 = self.uow.user.create(username="user_2")
        user_to_kick = self.uow.user.create(username="user_to_kick")
        team = self.create_team(members=[user_1, user_2, user_to_kick])
        expected = Result(
            data=None, error=exceptions.UserIsNotTeamLeaderException)
        result = services.kick_team_member_service(
            uow=self.uow, username='another_username', team_id=team.id, member_id=user_to_kick.id)
        self.assertEqual(expected, result)
