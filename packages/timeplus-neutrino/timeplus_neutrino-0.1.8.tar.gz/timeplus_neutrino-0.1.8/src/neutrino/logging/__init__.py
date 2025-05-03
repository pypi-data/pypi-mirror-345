import logging

from autogen_core import EVENT_LOGGER_NAME

from .handler import TimeplusHandler

logging.basicConfig(level=logging.WARNING)

event_logger = logging.getLogger(EVENT_LOGGER_NAME)
handler = TimeplusHandler()
event_logger.handlers = [handler]
event_logger.setLevel(logging.INFO)


def get_event_logger():
    return event_logger
