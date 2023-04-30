import json
from django.conf import settings
import service_layer.message_broker as mb
import service_layer.unit_of_work as uow
from service_layer.result import Result
import core.exceptions as exceptions
import core.logger as logger
import core.constants as constants


def create_team_service(uow: uow.AbstractUnitOfWork, username: str, event_id: int, **kwargs):
    with uow:
        if not kwargs.get('name', ''):
            return Result(None, error=exceptions.InvalidTeamDataException)
        event = uow.event.get(id=event_id)
        if event is None:
            return Result(data=None, error=exceptions.EventNotFoundException)
        team = uow.team.create(event=event, **kwargs)
        user = uow.user.get(username=username)
        uow.participant.create(
            user=user, team=team, role=constants.LEADER_ROLE, status=constants.APPLIED_STATUS)
        participants = uow.participant.list(team=team)
        return Result(data={**team.to_dict(), "participants": [participant.to_dict() for participant in participants]}, error=None)


def get_team_service(uow: uow.AbstractUnitOfWork, team_id: int):
    with uow:
        team = uow.team.get(id=team_id)
        if team is None:
            return Result(data=None, error=exceptions.TeamNotFoundException)
        participants = uow.participant.list(
            team=team, status=constants.APPLIED_STATUS)
        return Result(data={**team.to_dict(),
                            "participants": [participant.to_dict() for participant in participants]}, error=None)


def list_team_service(uow: uow.AbstractUnitOfWork, **kwargs):
    with uow:
        teams = uow.team.list(**kwargs)
        return Result(data=[team.to_dict() for team in teams], error=None)


def edit_team_service(uow: uow.AbstractUnitOfWork, username: str, team_id: int, **kwargs):
    with uow:
        if not kwargs.get('name', ''):
            return Result(None, error=exceptions.InvalidTeamDataException)
        team = uow.team.get(id=team_id)
        if team is None:
            return Result(data=None, error=exceptions.TeamNotFoundException)
        user = uow.user.get(username=username)
        leader = uow.participant.get(
            user=user, team=team, role=constants.LEADER_ROLE)
        if not leader or leader.user.username != username:
            return Result(data=None, error=exceptions.UserIsNotTeamLeaderException)
        team = uow.team.edit(id=team.id, **kwargs)
        participants = uow.participant.list(team=team)
        return Result(data={**team.to_dict(),
                            "participants": [participant.to_dict() for participant in participants]}, error=None)


def deactivate_team_service(uow: uow.AbstractUnitOfWork, username: str, team_id: int):
    with uow:
        team = uow.team.get(id=team_id)
        if team is None:
            return Result(data=None, error=exceptions.TeamNotFoundException)
        user = uow.user.get(username=username)
        leader = uow.participant.get(
            user=user, team=team, role=constants.LEADER_ROLE)
        if not leader or leader.user.username != username:
            return Result(data=None, error=exceptions.UserIsNotTeamLeaderException)
        team = uow.team.deactivate(id=team.id)
        participants = uow.participant.list(team=team)
        return Result(data={**team.to_dict(),
                            "participants": [participant.to_dict() for participant in participants]}, error=None)


def join_team_request_service(uow: uow.AbstractUnitOfWork, username: str, team_id: int):
    with uow:
        team = uow.team.get(id=team_id)
        if team is None:
            return Result(data=None, error=exceptions.TeamNotFoundException)
        user = uow.user.get(username=username)
        participant = uow.participant.get(user=user, team=team)
        if participant:
            return Result(data=None, error=exceptions.UserAlreadyHasParticipationException)
        participant = uow.participant.create(
            user=user, team=team, role=constants.MEMBER_ROLE, status=constants.PENDING_STATUS)
        # Notify Message Broker
        return Result(data=participant.to_dict(), error=None)


def change_team_participation_request_status_service(uow: uow.AbstractUnitOfWork, username: str, team_id: int, participant_id: int, status: str):
    with uow:
        if status not in constants.PARTICIPANT_STATUSES:
            return Result(data=None, error=exceptions.InvalidParticipantStatusException)
        team = uow.team.get(id=team_id)
        if team is None:
            return Result(data=None, error=exceptions.TeamNotFoundException)
        participant = uow.participant.get(id=participant_id)
        if not participant:
            return Result(data=None, error=exceptions.UserIsNotParticipantException)
        if participant.status == status:
            return Result(data=None, error=exceptions.ParticipantAlreadyHasStatusException)
        user = uow.user.get(username=username)
        leader = uow.participant.get(
            user=user, team=team, role=constants.LEADER_ROLE)
        if not leader:
            return Result(data=None, error=exceptions.UserIsNotTeamLeaderException)
        participant = uow.participant.edit(
            id=participant.id, status=status)
        # Notify Message Broker
        return Result(data=participant.to_dict(), error=None)


def kick_team_participant_service(uow: uow.AbstractUnitOfWork, username: str, team_id: int, participant_id: int):
    with uow:
        team = uow.team.get(id=team_id)
        if team is None:
            return Result(data=None, error=exceptions.TeamNotFoundException)
        participant = uow.participant.get(id=participant_id, team=team)
        if not participant:
            return Result(data=None, error=exceptions.UserIsNotParticipantException)
        user = uow.user.get(username=username)
        leader = uow.participant.get(
            user=user, team=team, role=constants.LEADER_ROLE)
        if not leader:
            return Result(data=None, error=exceptions.UserIsNotTeamLeaderException)
        participant = uow.participant.edit(
            id=participant.id, status=constants.KICKED_STATUS)
        # Notify Message Broker
        return Result(data=participant.to_dict(), error=None)


def handle_publish_message_on_user_kicked(user, team):
    try:
        if settings.DEBUG:
            message_broker = mb.RabbitMQ(
                exchange=settings.RABBITMQ_TEST_EXCHANGE_NAME)
        else:
            message_broker = mb.RabbitMQ()
        with message_broker:
            message_broker.publish(
                message=json.dumps({
                    "user": user,
                    "team": team,
                }), routing_key=settings.RABBITMQ_USER_KICKED_FROM_TEAM_ROUTING_KEY)
        logger.info(user='PUBLISHER',
                    message=f'Data({user} - {team}) sent to {settings.RABBITMQ_USER_KICKED_FROM_TEAM_ROUTING_KEY}', logger=logger.mb_logger)
    except Exception as e:
        logger.error(
            user='PUBLISHER', message=f'Error while publishing message on user {user} kicked from {team}: {e}', logger=logger.mb_logger)
