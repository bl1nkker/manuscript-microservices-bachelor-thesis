import json
import pika

from django.test import TestCase
from django.conf import settings

from service_layer.result import Result
import service_layer.services as services
import service_layer.unit_of_work as uow
import core.exceptions as exceptions
import service_layer.message_broker as mb
import core.constants as constants


class TestTeamServices(TestCase):
    def setUp(self) -> None:
        self.uow = uow.FakeUnitOfWork()
        self.user = self.uow.user.create(username="test", password="test")
        self.event = self.uow.event.create(name="test_event")
        return super().setUp()

    def create_team(self, name='test_team', event=None, user=None):
        if user is None:
            user = self.user
        if event is None:
            event = self.event
        team = self.uow.team.create(name=name, event=event, image='test_image')
        self.uow.participant.create(
            user=user, team=team, role=constants.LEADER_ROLE, status=constants.APPLIED_STATUS)
        return team

    # Create
    def test_create_team_service_should_create_team_and_return_result_with_team(self):
        body = {
            "name": 'test_team',
            "image": 'test_image',
        }
        expected = Result(data={
            "id": 1,
            "name": "test_team",
            "image": 'test_image',
            "event": self.event,
            "is_active": True,
            "participants": [
                {
                    'id': 1,
                    'user': self.user.to_dict(),
                    'team': {
                        'id': 1,
                        'name': 'test_team',
                        'image': 'test_image',
                        'event': self.event,
                        'is_active': True,
                    },
                    'role': constants.LEADER_ROLE,
                    'status': constants.APPLIED_STATUS,
                }
            ]
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

    def test_create_team_service_should_return_result_with_error_when_event_is_not_exists(self):
        body = {
            "name": 'test_team',
            "image": 'test_image',
        }
        expected = Result(data=None, error=exceptions.EventNotFoundException)
        result = services.create_team_service(
            uow=self.uow, event_id=999, username=self.user.username, **body)
        self.assertEqual(expected, result)

    # Get
    def test_get_team_service_should_return_result_with_team(self):
        team = self.create_team()
        expected = Result(data={
            "id": team.id,
            "name": "test_team",
            "image": 'test_image',
            "event": self.event,
            "is_active": True,
            "participants": [
                {
                    'id': 1,
                    'user': self.user.to_dict(),
                    'team': {
                        'id': 1,
                        'name': 'test_team',
                        'image': 'test_image',
                        'event': self.event,
                        'is_active': True,
                    },
                    'role': constants.LEADER_ROLE,
                    'status': constants.APPLIED_STATUS,
                }
            ]
        }, error=None)
        result = services.get_team_service(uow=self.uow, team_id=team.id)
        self.assertEqual(expected, result)

    def test_get_team_service_should_return_result_with_error_when_team_is_not_found(self):
        expected = Result(data=None, error=exceptions.TeamNotFoundException)
        result = services.get_team_service(uow=self.uow, team_id=999)
        self.assertEqual(expected, result)

    # # List
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

    # # Edit
    def test_edit_team_service_should_edit_team_and_return_result_with_team(self):
        team = self.create_team()
        expected = Result(data={
            "id": 1,
            "name": "updated event",
            "image": 'updated image',
            "event": self.event,
            "is_active": True,
            "participants": [
                {
                    'id': 1,
                    'user': self.user.to_dict(),
                    'team': {
                        'id': 1,
                        "name": "updated event",
                        "image": 'updated image',
                        'event': self.event,
                        'is_active': True,
                    },
                    'role': constants.LEADER_ROLE,
                    'status': constants.APPLIED_STATUS,
                }
            ]
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

    # # Deactivate
    def test_deactivate_team_service_should_deactivate_team_and_return_result_with_team(self):
        team = self.create_team()
        expected = Result(data={
            "id": 1,
            "name": "test_team",
            "image": 'test_image',
            "event": self.event,
            "is_active": False,
            "participants": [
                {
                    'id': 1,
                    'user': self.user.to_dict(),
                    'team': {
                        'id': 1,
                        "name": "test_team",
                        "image": 'test_image',
                        'event': self.event,
                        'is_active': False,
                    },
                    'role': constants.LEADER_ROLE,
                    'status': constants.APPLIED_STATUS,
                }
            ]
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

    # Join Request
    def test_join_team_request_service_should_return_result_with_pending_participation(self):
        team = self.create_team()
        another_user = self.uow.user.create(username="another_user")
        expected = Result(data={
            'id': 2,
            'user': another_user.to_dict(),
            'team': {
                'id': 1,
                "name": "test_team",
                "image": 'test_image',
                'event': self.event,
                'is_active': True,
            },
            'role': constants.MEMBER_ROLE,
            'status': constants.PENDING_STATUS,
        }, error=None)
        result = services.join_team_request_service(
            uow=self.uow, username=another_user.username, team_id=team.id)
        self.assertEqual(expected, result)

    def test_join_team_request_service_should_return_result_with_error_when_team_is_not_found(self):
        expected = Result(data=None, error=exceptions.TeamNotFoundException)
        result = services.join_team_request_service(
            uow=self.uow, username=self.user.username, team_id=999)
        self.assertEqual(expected, result)

    def test_join_team_request_service_should_return_result_with_error_when_user_already_has_participation(self):
        team = self.create_team()
        expected = Result(
            data=None, error=exceptions.UserAlreadyHasParticipationException)
        result = services.join_team_request_service(
            uow=self.uow, username=self.user.username, team_id=team.id)
        self.assertEqual(expected, result)

    # Apply/Decline
    def test_change_team_participation_service_should_return_result_with_applied_participation(self):
        team = self.create_team()
        another_user = self.uow.user.create(username="another_user")
        participant = self.uow.participant.create(
            user=another_user, team=team, status=constants.PENDING_STATUS, role=constants.MEMBER_ROLE)
        expected = Result(data={
            'id': 2,
            'user': another_user.to_dict(),
            'team': {
                'id': 1,
                "name": "test_team",
                "image": 'test_image',
                'event': self.event,
                'is_active': True,
            },
            'role': constants.MEMBER_ROLE,
            'status': constants.APPLIED_STATUS,
        }, error=None)
        result = services.change_team_participation_request_status_service(
            uow=self.uow, username=self.user.username, team_id=team.id, participant_id=participant.id, status=constants.APPLIED_STATUS)
        self.assertEqual(expected, result)
        another_user = self.uow.user.create(username="another_user")
        participant = self.uow.participant.create(
            user=another_user, team=team, status=constants.PENDING_STATUS, role=constants.MEMBER_ROLE)
        expected = Result(data={
            'id': 3,
            'user': another_user.to_dict(),
            'team': {
                'id': 1,
                "name": "test_team",
                "image": 'test_image',
                'event': self.event,
                'is_active': True,
            },
            'role': constants.MEMBER_ROLE,
            'status': constants.DECLINED_STATUS,
        }, error=None)
        result = services.change_team_participation_request_status_service(
            uow=self.uow, username=self.user.username, team_id=team.id, participant_id=participant.id, status=constants.DECLINED_STATUS)
        self.assertEqual(expected, result)

    def test_change_team_participation_service_should_return_result_with_error_when_team_is_not_found(self):
        expected = Result(data=None, error=exceptions.TeamNotFoundException)
        result = services.change_team_participation_request_status_service(
            uow=self.uow, username=self.user.username, team_id=999, participant_id=999, status=constants.APPLIED_STATUS)
        self.assertEqual(expected, result)

    def test_change_team_participation_service_should_return_result_with_error_when_participant_is_not_found(self):
        team = self.create_team()
        expected = Result(
            data=None, error=exceptions.UserIsNotParticipantException)
        result = services.change_team_participation_request_status_service(
            uow=self.uow, username=self.user.username, team_id=team.id, participant_id=999, status=constants.APPLIED_STATUS)
        self.assertEqual(expected, result)

    def test_change_team_participation_service_should_return_result_with_error_when_user_is_not_team_leader(self):
        team = self.create_team()
        another_user = self.uow.user.create(username="another_user")
        participant = self.uow.participant.create(
            user=another_user, team=team, status=constants.APPLIED_STATUS, role=constants.MEMBER_ROLE)
        expected = Result(
            data=None, error=exceptions.UserIsNotTeamLeaderException)
        result = services.change_team_participation_request_status_service(
            uow=self.uow, username=another_user.username, team_id=team.id, participant_id=participant.id, status=constants.PENDING_STATUS)
        self.assertEqual(expected, result)

    def test_change_team_participation_service_should_return_result_with_error_when_status_is_invalid(self):
        team = self.create_team()
        another_user = self.uow.user.create(username="another_user")
        participant = self.uow.participant.create(
            user=another_user, team=team, status=constants.APPLIED_STATUS, role=constants.MEMBER_ROLE)
        expected = Result(
            data=None, error=exceptions.InvalidParticipantStatusException)
        result = services.change_team_participation_request_status_service(
            uow=self.uow, username=self.user.username, team_id=team.id, participant_id=participant.id, status='invalid_status')
        self.assertEqual(expected, result)

    def test_change_team_participation_service_should_return_result_with_error_when_status_is_already_set(self):
        team = self.create_team()
        another_user = self.uow.user.create(username="another_user")
        participant = self.uow.participant.create(
            user=another_user, team=team, status=constants.APPLIED_STATUS, role=constants.MEMBER_ROLE)
        expected = Result(
            data=None, error=exceptions.ParticipantAlreadyHasStatusException)
        result = services.change_team_participation_request_status_service(
            uow=self.uow, username=self.user.username, team_id=team.id, participant_id=participant.id, status=constants.APPLIED_STATUS)
        self.assertEqual(expected, result)
    # Kick

    def test_kick_team_participant_service_should_return_result_with_kicked_participant(self):
        team = self.create_team()
        another_user = self.uow.user.create(username="another_user")
        participant = self.uow.participant.create(
            user=another_user, team=team, status=constants.APPLIED_STATUS, role=constants.MEMBER_ROLE)
        expected = Result(data={
            'id': 2,
            'user': another_user.to_dict(),
            'team': {
                'id': 1,
                "name": "test_team",
                "image": 'test_image',
                'event': self.event,
                'is_active': True,
            },
            'role': constants.MEMBER_ROLE,
            'status': constants.KICKED_STATUS,
        }, error=None)
        result = services.kick_team_participant_service(
            uow=self.uow, username=self.user.username, team_id=team.id, participant_id=participant.id)
        self.assertEqual(expected, result)

    def test_kick_team_participant_service_should_return_result_with_error_when_team_is_not_found(self):
        expected = Result(data=None, error=exceptions.TeamNotFoundException)
        result = services.kick_team_participant_service(
            uow=self.uow, username=self.user.username, team_id=999, participant_id=999)
        self.assertEqual(expected, result)

    def test_kick_team_participant_service_should_return_result_with_error_when_participant_is_not_found(self):
        team = self.create_team()
        expected = Result(
            data=None, error=exceptions.UserIsNotParticipantException)
        result = services.kick_team_participant_service(
            uow=self.uow, username=self.user.username, team_id=team.id, participant_id=999)
        self.assertEqual(expected, result)

    def test_kick_team_participant_service_should_return_result_with_error_when_user_is_not_team_leader(self):
        team = self.create_team()
        another_user = self.uow.user.create(username="another_user")
        participant = self.uow.participant.create(
            user=another_user, team=team, status=constants.APPLIED_STATUS, role=constants.MEMBER_ROLE)
        expected = Result(
            data=None, error=exceptions.UserIsNotTeamLeaderException)
        result = services.kick_team_participant_service(
            uow=self.uow, username=another_user.username, team_id=team.id, participant_id=participant.id)
        self.assertEqual(expected, result)

    # Leave
    def test_leave_team_service_should_return_result_with_left_participant(self):
        team = self.create_team()
        another_user = self.uow.user.create(username="another_user")
        self.uow.participant.create(
            user=another_user, team=team, status=constants.APPLIED_STATUS, role=constants.MEMBER_ROLE)
        expected = Result(data={
            'id': 2,
            'user': another_user.to_dict(),
            'team': {
                'id': 1,
                "name": "test_team",
                "image": 'test_image',
                'event': self.event,
                'is_active': True,
            },
            'role': constants.MEMBER_ROLE,
            'status': constants.LEFT_STATUS,
        }, error=None)
        result = services.leave_team_service(
            uow=self.uow, username=another_user.username, team_id=team.id)
        self.assertEqual(expected, result)
        team = self.uow.team.get(id=team.id)
        self.assertEqual(team.is_active, True)

    def test_leave_team_service_should_return_result_with_left_participant_and_deactivate_team_if_user_is_leader_and_there_are_no_other_participants(self):
        team = self.create_team()
        expected = Result(data={
            'id': 1,
            'user': self.user.to_dict(),
            'team': {
                'id': 1,
                "name": "test_team",
                "image": 'test_image',
                'event': self.event,
                'is_active': False,
            },
            'role': constants.LEADER_ROLE,
            'status': constants.LEFT_STATUS,
        }, error=None)
        result = services.leave_team_service(
            uow=self.uow, username=self.user.username, team_id=team.id)
        self.assertEqual(expected, result)
        team = self.uow.team.get(id=team.id)
        self.assertEqual(team.is_active, False)

    def test_leave_team_service_should_return_result_with_left_participant_and_set_another_participant_to_leader(self):
        team = self.create_team()
        another_user = self.uow.user.create(username="another_user")
        self.uow.participant.create(
            user=another_user, team=team, status=constants.APPLIED_STATUS, role=constants.MEMBER_ROLE)
        expected = Result(data={
            'id': 1,
            'user': self.user.to_dict(),
            'team': {
                'id': 1,
                "name": "test_team",
                "image": 'test_image',
                'event': self.event,
                'is_active': True,
            },
            'role': constants.LEADER_ROLE,
            'status': constants.LEFT_STATUS,
        }, error=None)
        result = services.leave_team_service(
            uow=self.uow, username=self.user.username, team_id=team.id)
        self.assertEqual(expected, result)
        team = self.uow.team.get(id=team.id)
        self.assertEqual(team.is_active, True)
        another_participant = self.uow.participant.get(
            user=another_user, team=team)
        self.assertEqual(another_participant.role, constants.LEADER_ROLE)

    def test_leave_team_service_should_return_result_with_error_when_team_is_not_found(self):
        expected = Result(data=None, error=exceptions.TeamNotFoundException)
        result = services.leave_team_service(
            uow=self.uow, username=self.user.username, team_id=999)
        self.assertEqual(expected, result)

    def test_leave_team_service_should_return_result_with_error_when_participant_is_not_found(self):
        team = self.create_team()
        another_user = self.uow.user.create(username="another_user")
        expected = Result(
            data=None, error=exceptions.UserIsNotParticipantException)
        result = services.leave_team_service(
            uow=self.uow, username=another_user.username, team_id=team.id)
        self.assertEqual(expected, result)
