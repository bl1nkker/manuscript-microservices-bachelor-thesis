UNKNOWN_EXCEPTION_MESSAGE = "Unknown error"
EVENT_NOT_FOUND_EXCEPTION_MESSAGE = "Event not found"
INVALID_EVENT_DATA_EXCEPTION_MESSAGE = "Invalid event data"
USER_IS_NOT_EVENT_AUTHOR_EXCEPTION_MESSAGE = "User is not event author"


class EventNotFoundException(Exception):
    message = EVENT_NOT_FOUND_EXCEPTION_MESSAGE


class InvalidEventDataException(Exception):
    message = INVALID_EVENT_DATA_EXCEPTION_MESSAGE


class UserIsNotEventAuthorException(Exception):
    message = USER_IS_NOT_EVENT_AUTHOR_EXCEPTION_MESSAGE
