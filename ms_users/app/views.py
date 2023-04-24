import json

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import service_layer.services as services
import service_layer.unit_of_work as uow
import core.exceptions as exceptions


@api_view(['POST'])
def register(request):
    body = request.data
    unit_of_work = uow.DjangoORMUnitOfWork()
    result = services.sign_up_user_service(
        uow=unit_of_work, request=request,
        first_name=body.get('first_name', ''),
        last_name=body.get('last_name', ''),
        username=body.get('email', ''),
        password=body.get('password', ''),
        confirm_password=body.get('confirm_password', ''))
    if result.is_ok:
        return Response(result.data, status=200)
    else:
        return Response({"message": exceptions.INVALID_USER_DATA_EXCEPTION_MESSAGE}, status=401)


@api_view(['POST'])
def login(request):
    body = request.data
    unit_of_work = uow.DjangoORMUnitOfWork()
    result = services.sign_in_user_service(uow=unit_of_work,
                                           request=request, username=body.get(
                                               'email', ''),
                                           password=body.get('password', ''),)
    if result.is_ok:
        return Response(result.data, status=200)
    else:
        return Response({"message": exceptions.AUTHENTICATION_EXCEPTION_MESSAGE}, status=401)


@api_view(['GET'])
def users(request, uid: int):
    unit_of_work = uow.DjangoORMUnitOfWork()
    result = services.get_user_service(
        uow=unit_of_work, uid=uid)
    if result.is_ok:
        return Response(result.data, status=200)
    else:
        return Response({"message": exceptions.USER_NOT_FOUND_EXCEPTION_MESSAGE}, status=404)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    unit_of_work = uow.DjangoORMUnitOfWork()
    result = services.get_me_service(
        uow=unit_of_work, user=request.user)
    if result.is_ok:
        return Response(result.data, status=200)
    else:
        return Response({"message": exceptions.USER_NOT_FOUND_EXCEPTION_MESSAGE}, status=404)
