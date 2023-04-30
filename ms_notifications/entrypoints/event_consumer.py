import json
import service_layer.message_broker as mb
import app.models as models
from django.conf import settings
import os
import core.logger as logger
import core.constants as constants
os.environ['DJANGO_SETTINGS_MODULE'] = 'ms_notifications.settings'


def start(message_broker):
    logger.info(user='CONSUMER',
                message='Starting message broker connection...', logger=logger.mb_logger)
    try:
        with message_broker:
            message_broker.subscribe(
                queue=settings.RABBITMQ_QUEUE, callback=handle_user_creation, routing_key=settings.RABBITMQ_USER_CREATE_ROUTING_KEY)
            message_broker.subscribe(
                queue=settings.RABBITMQ_QUEUE, callback=handle_user_left_from_team, routing_key=settings.RABBITMQ_USER_LEFT_FROM_TEAM_ROUTING_KEY)
            message_broker.subscribe(
                queue=settings.RABBITMQ_QUEUE, callback=handle_user_join_request, routing_key=settings.RABBITMQ_USER_JOIN_REQUEST_ROUTING_KEY)
            message_broker.subscribe(
                queue=settings.RABBITMQ_QUEUE, callback=handle_user_join_request_updated, routing_key=settings.RABBITMQ_USER_JOIN_REQUEST_UPDATED_ROUTING_KEY)
            message_broker.subscribe(
                queue=settings.RABBITMQ_QUEUE, callback=handle_user_kicked_from_team, routing_key=settings.RABBITMQ_USER_KICKED_FROM_TEAM_ROUTING_KEY)
            message_broker.start_consuming()
    except Exception as e:
        logger.error(user='CONSUMER',
                     message=f'Error while consuming message: {e}', logger=logger.mb_logger)
    finally:
        logger.info(user='CONSUMER',
                    message='Closing message broker connection...', logger=logger.mb_logger)


def handle_user_creation(ch, method, properties, body):
    logger.info(user='CONSUMER',
                message=f'Handle user creation with body: {body}', logger=logger.mb_logger)
    data = json.loads(body)
    import django
    django.setup()
    user = models.User.objects.create(
        username=data['username'],
        email=data['username'],
        first_name=data['first_name'],
        last_name=data['last_name'],
    )
    models.ManuscriptUser.objects.create(
        id=data['id'],
        user=user
    )
    logger.info(user='CONSUMER',
                message=f'User created: {user}', logger=logger.mb_logger)


def handle_user_join_request(ch, method, properties, body):
    logger.info(user='CONSUMER',
                message=f'Handle user join request with body: {body}', logger=logger.mb_logger)
    data = json.loads(body)
    import django
    django.setup()
    user = models.ManuscriptUser.objects.get(id=data['user']['id'])
    notification = models.Notification.objects.create(
        user=user, message='Join request sent', status=constants.SUCCESS_TYPE)
    logger.info(user='CONSUMER',
                message=f'Notification created: {notification.to_dict()}', logger=logger.mb_logger)


def handle_user_left_from_team(ch, method, properties, body):
    logger.info(user='CONSUMER',
                message=f'Handle user left from team with body: {body}', logger=logger.mb_logger)
    data = json.loads(body)
    import django
    django.setup()
    user = models.ManuscriptUser.objects.get(id=data['user']['id'])
    notification = models.Notification.objects.create(
        user=user, message='User left from team', status=constants.SUCCESS_TYPE)
    logger.info(user='CONSUMER',
                message=f'Notification created: {notification.to_dict()}', logger=logger.mb_logger)


def handle_user_join_request_updated(ch, method, properties, body):
    logger.info(user='CONSUMER',
                message=f'Handle user join request updated with body: {body}', logger=logger.mb_logger)
    data = json.loads(body)
    import django
    django.setup()
    user = models.ManuscriptUser.objects.get(id=data['user']['id'])
    notification = models.Notification.objects.create(
        user=user, message='Join request updated', status=constants.WARNING_TYPE)
    logger.info(user='CONSUMER',
                message=f'Notification created: {notification.to_dict()}', logger=logger.mb_logger)


def handle_user_kicked_from_team(ch, method, properties, body):
    logger.info(user='CONSUMER',
                message=f'Handle user kicked from team with body: {body}', logger=logger.mb_logger)
    data = json.loads(body)
    import django
    django.setup()
    user = models.ManuscriptUser.objects.get(id=data['user']['id'])
    notification = models.Notification.objects.create(
        user=user, message='User kicked from team', status=constants.DANGER_TYPE)
    logger.info(user='CONSUMER',
                message=f'Notification created: {notification.to_dict()}', logger=logger.mb_logger)


if __name__ == '__main__':
    message_broker = mb.RabbitMQ()
    start(message_broker=message_broker)
