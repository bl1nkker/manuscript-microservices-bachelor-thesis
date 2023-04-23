import json

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
import service_layer.services as services
import service_layer.unit_of_work as unit_of_work

# Create your views here.


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def teams(request):
    uow = unit_of_work.DjangoORMUnitOfWork()
    if request.method == 'POST':
        body = {}
        for key, value in request.data.items():
            body[key] = value
        event_id = request.query_params.get('event_id', None)
        username = request.user.username
        result = services.create_team_service(
            uow=uow, event_id=event_id, username=username, **body)
        if result.is_ok:
            return Response(result.to_response(), status=201)
        else:
            return Response(result.to_response(), status=401)
    elif request.method == 'GET':
        filter_params = {key: value
                         for key, value in request.query_params.items()}
        result = services.list_team_service(uow=uow, **filter_params)
        if result.is_ok:
            return Response(result.to_response(), status=200)
        else:
            return Response(result.to_response(), status=401)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticatedOrReadOnly])
def team(request, team_id: int):
    uow = unit_of_work.DjangoORMUnitOfWork()
    if request.method == 'GET':
        result = services.get_team_service(uow, team_id=team_id)
        if result.is_ok:
            return Response(result.to_response(), status=200)
        else:
            return Response(result.to_response(), status=404)
    elif request.method == 'PUT':
        body = {}
        for key, value in request.data.items():
            body[key] = value
        username = request.user.username
        result = services.edit_team_service(
            uow=uow, team_id=team_id, username=username, **body)
        if result.is_ok:
            return Response(result.to_response(), status=204)
        else:
            return Response(result.to_response(), status=401)
    elif request.method == 'DELETE':
        username = request.user.username
        result = services.deactivate_team_service(
            uow=uow, team_id=team_id, username=username)
        if result.is_ok:
            return Response(result.to_response(), status=204)
        else:
            return Response(result.to_response(), status=401)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def kick(request, team_id: int, member_id: int):
    uow = unit_of_work.DjangoORMUnitOfWork()
    if request.method == 'GET':
        username = request.user.username
        result = services.kick_team_member_service(
            uow=uow, team_id=team_id, username=username, member_id=member_id)
        if result.is_ok:
            return Response(result.to_response(), status=200)
        else:
            return Response(result.to_response(), status=401)
