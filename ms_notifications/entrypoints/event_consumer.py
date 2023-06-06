import os
import json
os.environ['DJANGO_SETTINGS_MODULE'] = 'ms_notifications.settings'
import django
django.setup()
import core.constants as constants
import core.logger as logger
from django.conf import settings
import app.models as models
import service_layer.message_broker as mb


def start(message_broker: mb.RabbitMQ):
    logger.info(user='CONSUMER',
                message='Starting message broker connection...', logger=logger.mb_logger)
    try:
        binds = [
                (settings.RABBITMQ_QUEUE_USER_CREATED, settings.RABBITMQ_USER_CREATE_ROUTING_KEY, handle_user_creation),
                (settings.RABBITMQ_QUEUE_USER_LEFT_FROM_TEAM, settings.RABBITMQ_USER_LEFT_FROM_TEAM_ROUTING_KEY, handle_user_left_from_team),
                (settings.RABBITMQ_QUEUE_USER_JOIN_REQUEST, settings.RABBITMQ_USER_JOIN_REQUEST_ROUTING_KEY, handle_user_join_request),
                (settings.RABBITMQ_QUEUE_USER_JOIN_REQUEST_UPDATED, settings.RABBITMQ_USER_JOIN_REQUEST_UPDATED_ROUTING_KEY, handle_user_join_request_updated),
                (settings.RABBITMQ_QUEUE_USER_KICKED_FROM_TEAM, settings.RABBITMQ_USER_KICKED_FROM_TEAM_ROUTING_KEY, handle_user_kicked_from_team),
        ]
        with message_broker:
            for item in binds:
                (queue, routing_key, callback) = item
                message_broker.channel.queue_declare(queue=queue, durable=True)
                message_broker.queue_bind(queue=queue, routing_key=routing_key)
                message_broker.channel.basic_consume(
                    queue=queue, on_message_callback=callback, auto_ack=True)
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
    for uid in data['to']:
        user = data['user']['username']
        team = data['team']['name']
        to = models.ManuscriptUser.objects.get(id=uid)
        models.Notification.objects.create(
            user=to, message=f'Пользователь {user} отправил запрос на присоединение к команде {team}', status=constants.WARNING_TYPE)
    logger.info(user='CONSUMER',
                message=f'Notifications created to {data["to"]}', logger=logger.mb_logger)


def handle_user_left_from_team(ch, method, properties, body):
    logger.info(user='CONSUMER',
                message=f'Handle user left from team with body: {body}', logger=logger.mb_logger)
    data = json.loads(body)
    for uid in data['to']:
        user = data['user']['username']
        team = data['team']['name']
        to = models.ManuscriptUser.objects.get(id=uid)
        models.Notification.objects.create(
            user=to, message=f'Пользователь {user} вышел из команды {team}', status=constants.WARNING_TYPE)
    logger.info(user='CONSUMER',
                message=f'Notifications created to {data["to"]}', logger=logger.mb_logger)


def handle_user_join_request_updated(ch, method, properties, body):
    logger.info(user='CONSUMER',
                message=f'Handle user join request updated with body: {body}', logger=logger.mb_logger)
    data = json.loads(body)
    for uid in data['to']:
        user = data['user']['username']
        team = data['team']['name']
        to = models.ManuscriptUser.objects.get(id=uid)
        models.Notification.objects.create(
            user=to, message=f'Пользователь {to.user.username} был {data["action"]} в команде {team} пользователем {user}', status=constants.WARNING_TYPE)
    logger.info(user='CONSUMER',
                message=f'Notifications created to {data["to"]}', logger=logger.mb_logger)


def handle_user_kicked_from_team(ch, method, properties, body):
    logger.info(user='CONSUMER',
                message=f'Handle user kicked from team with body: {body}', logger=logger.mb_logger)
    data = json.loads(body)
    for uid in data['to']:
        user = data['user']['username']
        team = data['team']['name']
        to = models.ManuscriptUser.objects.get(id=uid)
        models.Notification.objects.create(
        user=to, message=f'Пользователь {to.user.username} исключен из команды {team} пользователем {user}', status=constants.DANGER_TYPE)
    logger.info(user='CONSUMER',
                message=f'Notifications created to {data["to"]}', logger=logger.mb_logger)

if __name__ == '__main__':
    message_broker = mb.RabbitMQ()
    start(message_broker=message_broker)
