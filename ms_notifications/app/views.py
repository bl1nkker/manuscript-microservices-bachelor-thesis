from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
import service_layer.services as services
import service_layer.unit_of_work as unit_of_work
import core.logger as logger
import core.constants as constants


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notifications(request):
    uow = unit_of_work.DjangoORMUnitOfWork()
    if request.method == 'GET':
        logger.info(request.user, "GET /notifications")
        username = request.user.username
        result = services.list_notifications_service(
            uow=uow, username=username)
        if result.is_ok:
            logger.info(request.user, "GET /notifications SUCCESS")
            return Response(result.to_response(), status=200)
        else:
            logger.warning(
                request.user, f"GET /notifications FAIL: {result.to_response()}")
            return Response(result.to_response(), status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notification(request, notification_id: int):
    uow = unit_of_work.DjangoORMUnitOfWork()
    if request.method == 'GET':
        logger.info(request.user, "GET /notifications")
        username = request.user.username
        result = services.get_notification_service(
            uow=uow, username=username, id=notification_id)
        if result.is_ok:
            logger.info(request.user, "GET /notifications SUCCESS")
            return Response(result.to_response(), status=200)
        else:
            logger.warning(
                request.user, f"GET /notifications FAIL: {result.to_response()}")
            return Response(result.to_response(), status=400)
