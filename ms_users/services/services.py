from services import Result
import services.unit_of_work as uow
import core.exceptions as exceptions


def sign_in_user_service(uow: uow.AbstractUnitOfWork, request, username: str, password: str) -> Result:
    with uow:
        if uow.user.authenticate(request=request, username=username, password=password) is None:
            return Result(data=None, error=exceptions.AuthenticationException)
        m_user = uow.user.get(username=username)
    return Result(data={"access_token": m_user.generate_jwt_token()})


def sign_up_user_service(uow: uow.AbstractUnitOfWork, request, username: str, first_name: str, last_name: str, password: str, confirm_password: str) -> Result:
    if password != confirm_password:
        return Result(data=None, error=exceptions.InvalidUserDataException)
    if not username or not first_name or not last_name:
        return Result(data=None, error=exceptions.InvalidUserDataException)
    with uow:
        user = uow.user.create(username=username, first_name=first_name,
                               last_name=last_name, password=password, email=username)
    try:
        handle_publish_message_on_user_created(user=user)
    except Exception as e:
        print('Error while publishing message: ', e)
    return Result(data={"access_token": user.generate_jwt_token()})


def get_user_service(uow: uow.AbstractUnitOfWork, uid: int = None) -> Result:
    with uow:
        user = uow.user.get(id=uid)
        if user is None:
            return Result(data=None, error=exceptions.UserNotFoundException)
    return Result(data=user.to_dict(), error=None)


def get_me_service(uow: uow.AbstractUnitOfWork, user) -> Result:
    with uow:
        m_user = uow.user.get(username=user.username)
        return Result(data=m_user.to_dict(), error=None)


def handle_publish_message_on_user_created(user):
    import pika
    import json
    from django.conf import settings
    import services.message_broker as mb
    credentials = pika.URLParameters(settings.RABBITMQ_CONNECTION_URL)
    message_broker = mb.RabbitMQ(
        credentials.host, credentials.port, credentials.credentials.username, credentials.credentials.password, exchange=settings.RABBITMQ_EXCHANGE_NAME)
    print('Connecting to message broker...')
    with message_broker:
        print('Publishing message...')
        message_broker.publish(
            message=json.dumps(user.to_dict()), routing_key=settings.RABBITMQ_USER_CREATE_ROUTING_KEY)
