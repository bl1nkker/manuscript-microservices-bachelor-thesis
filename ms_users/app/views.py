import json
import pika

from django.contrib.auth import authenticate, login, hashers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.conf import settings
import app.models as models
import service_layer.message_broker as mb


@api_view(['POST'])
def register(request):
    # TODO: Add second password field to check if they match
    body = json.loads(request.body.decode('utf-8'))
    hashed_password = hashers.make_password(body['password'])
    models.User.objects.create(
        email=body['email'],
        username=body['email'],
        first_name=body['first_name'],
        last_name=body['last_name'],
        password=hashed_password
    )

    user = authenticate(
        request, username=body['email'], password=body['password'])
    user = models.ManuscriptUser.objects.create(user=user)
    credentials = pika.URLParameters(settings.RABBITMQ_CONNECTION_URL)
    message_broker = mb.RabbitMQ(
        credentials.host, credentials.port, credentials.credentials.username, credentials.credentials.password, exchange=settings.RABBITMQ_EXCHANGE_NAME)
    with message_broker:
        message_broker.publish(
            message=json.dumps(user.to_dict()), routing_key=settings.RABBITMQ_USER_CREATE_ROUTING_KEY)
    return Response({"user": user.to_dict(), "token": user.generate_jwt_token()}, status=201)


@api_view(['POST'])
def login(request):
    body = json.loads(request.body.decode('utf-8'))
    user = authenticate(
        request, username=body['email'], password=body['password'])

    user = models.ManuscriptUser.objects.get(user=user)
    return Response({"user": user.to_dict(), "token": user.generate_jwt_token()}, status=200)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def users(request):
    users = models.ManuscriptUser.objects.all()
    return Response({"users": [user.to_dict() for user in users]}, status=200)
