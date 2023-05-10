import telebot
import os
import message_broker as mb

with open('app.yaml') as f:
    import yaml
    settings = yaml.safe_load(f)

bot = telebot.TeleBot(settings['TELEGRAM_TOKEN'])

# Определяем обработчик сообщений из очереди


def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)
    message = 'Hello, world!'
    body = body.decode()
    if method.routing_key == settings['RABBITMQ_USER_CREATE_ROUTING_KEY']:
        message = f'User created: {body}'
    elif method.routing_key == settings['RABBITMQ_EVENT_EDIT_ROUTING_KEY']:
        message = f'Event edited: {body}'
    elif method.routing_key == settings['RABBITMQ_EVENT_CREATE_ROUTING_KEY']:
        message = f'Event created: {body}'
    elif method.routing_key == settings['RABBITMQ_USER_LEFT_FROM_TEAM_ROUTING_KEY']:
        message = f'User left from team: {body}'
    elif method.routing_key == settings['RABBITMQ_USER_JOIN_REQUEST_ROUTING_KEY']:
        message = f'User join request: {body}'
    elif method.routing_key == settings['RABBITMQ_USER_JOIN_REQUEST_UPDATED_ROUTING_KEY']:
        message = f'User join request updated: {body}'
    elif method.routing_key == settings['RABBITMQ_USER_KICKED_FROM_TEAM_ROUTING_KEY']:
        message = f'User kicked from team: {body}'
    receivers = ['858128787']
    for chat in receivers:
        bot.send_message(chat_id=chat, text=message)


# Создаем соединение с RabbitMQ
rabbitmq = mb.RabbitMQ()
with rabbitmq:
    rabbitmq.subscribe(queue='telegram', callback=callback,
                       routing_key=settings['RABBITMQ_USER_CREATE_ROUTING_KEY'])
    rabbitmq.subscribe(queue='telegram', callback=callback,
                       routing_key=settings['RABBITMQ_EVENT_EDIT_ROUTING_KEY'])
    rabbitmq.subscribe(queue='telegram', callback=callback,
                       routing_key=settings['RABBITMQ_EVENT_CREATE_ROUTING_KEY'])
    rabbitmq.subscribe(queue='telegram', callback=callback,
                       routing_key=settings['RABBITMQ_USER_LEFT_FROM_TEAM_ROUTING_KEY'])
    rabbitmq.subscribe(queue='telegram', callback=callback,
                       routing_key=settings['RABBITMQ_USER_JOIN_REQUEST_ROUTING_KEY'])
    rabbitmq.subscribe(queue='telegram', callback=callback,
                       routing_key=settings['RABBITMQ_USER_JOIN_REQUEST_UPDATED_ROUTING_KEY'])
    rabbitmq.subscribe(queue='telegram', callback=callback,
                       routing_key=settings['RABBITMQ_USER_KICKED_FROM_TEAM_ROUTING_KEY'])
    rabbitmq.start_consuming()
