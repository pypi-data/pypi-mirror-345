import os

from loguru import logger

from ..config import settings

logger.remove()

default_logger_file = os.path.join(
    os.path.expanduser("~"), ".sdk_download/download.log"
)
default_logger_format = "{time:HH:mm:ss} {level} {thread.name} {message}"


def init():
    conf = settings.Application()

    if conf.level == "DEBUG":
        logger.add(lambda msg: print(msg, end=""), level=conf.level, colorize=True)

    logger.add(
        default_logger_file,
        format=default_logger_format,
        encoding="utf-8",
        level="INFO",
    )
