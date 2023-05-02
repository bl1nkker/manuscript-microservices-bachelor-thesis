from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
import service_layer.services as services
import service_layer.unit_of_work as unit_of_work
import core.logger as logger


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def teams(request):
    uow = unit_of_work.DjangoORMUnitOfWork()
    if request.method == 'POST':
        logger.info(request.user, "POST /teams")
        body = {}
        for key, value in request.data.items():
            body[key] = value
        event_id = request.query_params.get('event_id', None)
        username = request.user.username
        result = services.create_team_service(
            uow=uow, event_id=event_id, username=username, **body)
        if result.is_ok:
            logger.info(request.user, "POST /teams SUCCESS")
            return Response(result.to_response(), status=201)
        else:
            logger.warning(
                request.user, f"POST /teams FAIL: {result.to_response()}")
            return Response(result.to_response(), status=400)
    elif request.method == 'GET':
        logger.info(request.user, "GET /teams")
        filter_params = {key: value
                         for key, value in request.query_params.items()}
        result = services.list_team_service(uow=uow, **filter_params)
        if result.is_ok:
            logger.info(request.user, "GET /teams SUCCESS")
            return Response(result.to_response(), status=200)
        else:
            logger.warning(
                request.user, f"GET /teams FAIL: {result.to_response()}")
            return Response(result.to_response(), status=400)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticatedOrReadOnly])
def team(request, team_id: int):
    uow = unit_of_work.DjangoORMUnitOfWork()
    if request.method == 'GET':
        logger.info(request.user, f"GET /teams/{team_id}")
        result = services.get_team_service(uow, team_id=team_id)
        if result.is_ok:
            logger.info(request.user, f"GET /teams/{team_id} SUCCESS")
            return Response(result.to_response(), status=200)
        else:
            logger.warning(
                request.user, f"GET /teams/{team_id} FAIL {result.to_response()}")
            return Response(result.to_response(), status=404)
    elif request.method == 'PUT':
        logger.info(request.user, f"PUT /teams/{team_id}")
        body = {}
        for key, value in request.data.items():
            body[key] = value
        username = request.user.username
        result = services.edit_team_service(
            uow=uow, team_id=team_id, username=username, **body)
        if result.is_ok:
            logger.info(request.user, f"PUT /teams/{team_id} SUCCESS")
            return Response(result.to_response(), status=200)
        else:
            logger.warning(
                request.user, f"PUT /teams/{team_id} FAIL {result.to_response()}")
            return Response(result.to_response(), status=400)
    elif request.method == 'DELETE':
        logger.info(request.user, f"DELETE /teams/{team_id}")
        username = request.user.username
        result = services.deactivate_team_service(
            uow=uow, team_id=team_id, username=username)
        if result.is_ok:
            logger.info(request.user, f"DELETE /teams/{team_id} SUCCESS")
            return Response(result.to_response(), status=200)
        else:
            logger.warning(
                request.user, f"DELETE /teams/{team_id} FAIL {result.to_response()}")
            return Response(result.to_response(), status=400)


@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def team_participants(request, team_id: int):
    uow = unit_of_work.DjangoORMUnitOfWork()
    if request.method == 'POST':
        logger.info(request.user, f"POST /teams/{team_id}/participants")
        result = services.join_team_request_service(
            uow, team_id=team_id, username=request.user.username)
        if result.is_ok:
            logger.info(
                request.user, f"POST /teams/{team_id}/participants SUCCESS")
            return Response(result.to_response(), status=201)
        else:
            logger.warning(
                request.user, f"POST /teams/{team_id}/participants FAIL {result.to_response()}")
            return Response(result.to_response(), status=400)
    elif request.method == 'DELETE':
        logger.info(request.user, f"DELETE /teams/{team_id}/participants")
        result = services.leave_team_service(
            uow, team_id=team_id, username=request.user.username)
        if result.is_ok:
            logger.info(
                request.user, f"DELETE /teams/{team_id}/participants SUCCESS")
            return Response(result.to_response(), status=200)
        else:
            logger.warning(
                request.user, f"DELETE /teams/{team_id}/participants FAIL {result.to_response()}")
            return Response(result.to_response(), status=400)


@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def team_participant(request, team_id: int, participant_id: int):
    uow = unit_of_work.DjangoORMUnitOfWork()
    if request.method == 'PUT':
        logger.info(
            request.user, f"PUT /teams/{team_id}/participants/{participant_id}")
        username = request.user.username
        status = request.data.get('status', None)
        result = services.change_team_participation_request_status_service(
            uow, username=username, team_id=team_id, participant_id=participant_id, status=status)
        if result.is_ok:
            logger.info(
                request.user, f"PUT /teams/{team_id}/participants/{participant_id} SUCCESS")
            return Response(result.to_response(), status=200)
        else:
            logger.warning(
                request.user, f"PUT /teams/{team_id}/participants/{participant_id} FAIL {result.to_response()}")
            return Response(result.to_response(), status=400)
    elif request.method == 'DELETE':
        logger.info(
            request.user, f"DELETE /teams/{team_id}/participants/{participant_id}")
        username = request.user.username
        result = services.kick_team_participant_service(
            uow, username=username, team_id=team_id, participant_id=participant_id)
        if result.is_ok:
            logger.info(
                request.user, f"DELETE /teams/{team_id}/participants/{participant_id} SUCCESS")
            return Response(result.to_response(), status=200)
        else:
            logger.warning(
                request.user, f"DELETE /teams/{team_id}/participants/{participant_id} FAIL {result.to_response()}")
            return Response(result.to_response(), status=400)
