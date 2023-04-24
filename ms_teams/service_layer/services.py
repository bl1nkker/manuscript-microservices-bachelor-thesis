import json
from django.conf import settings
import service_layer.message_broker as mb
import service_layer.unit_of_work as uow
from service_layer.result import Result
import core.exceptions as exceptions
import core.logger as logger


def create_team_service(uow: uow.AbstractUnitOfWork, username: str, event_id: int, **kwargs):
    with uow:
        if not kwargs.get('name', ''):
            return Result(None, error=exceptions.InvalidTeamDataException)
        event = uow.event.get(id=event_id)
        if event is None:
            return Result(data=None, error=exceptions.EventNotFoundException)
        user = uow.user.get(username=username)
        team = uow.team.create(leader=user, event=event, **kwargs)
        return Result(data=team.to_dict(), error=None)


def get_team_service(uow: uow.AbstractUnitOfWork, team_id: int):
    with uow:
        team = uow.team.get(id=team_id)
        if team is None:
            return Result(data=None, error=exceptions.TeamNotFoundException)
        return Result(data=team.to_dict(), error=None)


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
        if team.leader.username != username:
            return Result(data=None, error=exceptions.UserIsNotTeamLeaderException)
        team = uow.team.edit(id=team.id, **kwargs)
        return Result(data=team.to_dict(), error=None)


def deactivate_team_service(uow: uow.AbstractUnitOfWork, username: str, team_id: int):
    with uow:
        team = uow.team.get(id=team_id)
        if team is None:
            return Result(data=None, error=exceptions.TeamNotFoundException)
        if team.leader.username != username:
            return Result(data=None, error=exceptions.UserIsNotTeamLeaderException)
        team = uow.team.deactivate(id=team.id)
        return Result(data=team.to_dict(), error=None)


def kick_team_member_service(uow: uow.AbstractUnitOfWork, username: str, team_id: int, member_id: int):
    with uow:
        team = uow.team.get(id=team_id)
        if team is None:
            return Result(data=None, error=exceptions.TeamNotFoundException)
        if team.leader.username != username:
            return Result(data=None, error=exceptions.UserIsNotTeamLeaderException)
        updated_members = [
            member for member in team.get_members() if member.id != member_id]
        team = uow.team.edit(id=team.id, members=updated_members)
        # try:
        #     handle_publish_message_on_user_kicked(user=member_id, team=team.id)
        # except Exception as e:
        #     print('Error while publishing message', e)
        return Result(data=team.to_dict(), error=None)


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
