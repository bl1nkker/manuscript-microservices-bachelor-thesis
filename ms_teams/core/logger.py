import logging
import datetime
app_logger = logging.getLogger("manuscript")
mb_logger = logging.getLogger("rabbitmq")


def debug(user, message, logger=app_logger):
    logger.debug(
        f"[{datetime.datetime.now().strftime('%-d %B %Y, %H:%M:%S')}] {user}: {message}")


def info(user, message, logger=app_logger):
    logger.info(
        f"[{datetime.datetime.now().strftime('%-d %B %Y, %H:%M:%S')} {user}: {message}]")


def warning(user, message, logger=app_logger):
    logger.warning(
        f"[{datetime.datetime.now().strftime('%-d %B %Y, %H:%M:%S')} {user}: {message}]")


def error(user, message, logger=app_logger):
    logger.error(
        f"[{datetime.datetime.now().strftime('%-d %B %Y, %H:%M:%S')} {user}: {message}]")


def critical(user, message, logger=app_logger):
    logger.critical(
        f"[{datetime.datetime.now().strftime('%-d %B %Y, %H:%M:%S')} {user}: {message}]")
