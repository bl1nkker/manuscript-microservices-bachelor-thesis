import service_layer.message_broker as mb
from django.conf import settings
import pika
import json
import os
import core.logger as logger
os.environ['DJANGO_SETTINGS_MODULE'] = 'ms_event.settings'


def start(message_broker):
    logger.info(user='CONSUMER',
                message='Starting message broker connection...', logger=logger.mb_logger)
    try:
        pass
    except Exception as e:
        logger.error(user='CONSUMER',
                     message=f'Error while consuming message: {e}', logger=logger.mb_logger)
    finally:
        logger.info(user='CONSUMER',
                    message='Closing message broker connection...', logger=logger.mb_logger)


if __name__ == '__main__':
    message_broker = mb.RabbitMQ()
    start(message_broker=message_broker)
