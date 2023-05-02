from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
import service_layer.services as services
import service_layer.unit_of_work as unit_of_work
import core.logger as logger


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def events(request):
    uow = unit_of_work.DjangoORMUnitOfWork()
    try:
        if request.method == 'GET':
            logger.info(request.user, "GET /events")
            filter_params = {key: value
                             for key, value in request.query_params.items()}
            result = services.list_events_service(uow=uow, **filter_params)
            if result.is_ok:
                logger.info(request.user, "GET /events SUCCESS")
                return Response(result.to_response(), status=200)
            else:
                logger.warning(
                    request.user, f"GET /events FAIL: {result.to_response()}")
                return Response(result.to_response(), status=400)
        elif request.method == 'POST':
            logger.info(request.user, "POST /events")
            body = {}
            for key, value in request.data.items():
                if key == 'tags':
                    body['tags'] = request.data.getlist(key, [])
                    continue
                body[key] = value

            username = request.user.username
            result = services.create_event_service(
                uow=uow, username=username, **body)
            if result.is_ok:
                logger.info(request.user, "POST /events SUCCESS")
                return Response(result.to_response(), status=201)
            else:
                logger.warning(
                    request.user, f"POST /events FAIL: {result.to_response()}")
                return Response(result.to_response(), status=400)
    except Exception as e:
        logger.error(request.user, f"{request.method} /events ERROR: {e}")
        return Response({"message": "Unknown error"}, status=400)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticatedOrReadOnly])
def event(request, event_id):
    uow = unit_of_work.DjangoORMUnitOfWork()
    try:
        if request.method == 'GET':
            logger.info(request.user, f"GET /events/{event_id}")
            result = services.get_event_service(uow, id=event_id)
            if result.is_ok:
                logger.info(request.user, f"GET /events/{event_id} SUCCESS")
                return Response(result.to_response(), status=200)
            else:
                logger.warning(
                    request.user, f"GET /events/{event_id} FAIL {result.to_response()}")
                return Response(result.to_response(), status=404)
        elif request.method == 'PUT':
            logger.info(request.user, f"PUT /events/{event_id}")
            body = {}
            for key, value in request.data.items():
                if key == 'tags':
                    body['tags'] = request.data.getlist(key, [])
                    continue
                body[key] = value
            username = request.user.username
            result = services.edit_event_service(
                uow=uow, id=event_id, username=username, **body)
            if result.is_ok:
                logger.info(request.user, f"PUT /events/{event_id} SUCCESS")
                return Response(result.to_response(), status=200)
            else:
                logger.warning(
                    request.user, f"PUT /events/{event_id} FAIL {result.to_response()}")
                return Response(result.to_response(), status=400)
        elif request.method == 'DELETE':
            username = request.user.username
            result = services.deactivate_event_service(
                uow=uow, id=event_id, username=username)
            if result.is_ok:
                logger.info(request.user, f"DELETE /events/{event_id} SUCCESS")
                return Response(result.to_response(), status=200)
            else:
                logger.warning(
                    request.user, f"DELETE /events/{event_id} FAIL {result.to_response()}")
                return Response(result.to_response(), status=400)
    except Exception as e:
        logger.error(
            request.user, f"{request.method} /events/{event_id} ERROR: {e}")
        return Response({"message": "Unknown error"}, status=400)
