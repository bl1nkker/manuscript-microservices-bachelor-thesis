EVENT_NOT_FOUND_EXCEPTION_MESSAGE = "Event not found"
INVALID_EVENT_DATA_EXCEPTION_MESSAGE = "Invalid event data"


class EventNotFoundException(Exception):
    message = EVENT_NOT_FOUND_EXCEPTION_MESSAGE


class InvalidEventDataException(Exception):
    message = INVALID_EVENT_DATA_EXCEPTION_MESSAGE
