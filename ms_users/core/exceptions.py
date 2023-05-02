''' Exceptions for the services '''
UNKNOWN_EXCEPTION_MESSAGE = "Unknown error"
AUTHENTICATION_EXCEPTION_MESSAGE = "Username or password is incorrect"
INVALID_USER_DATA_EXCEPTION_MESSAGE = "Invalid user data"
USER_NOT_FOUND_EXCEPTION_MESSAGE = "User not found"


class AuthenticationException(Exception):
    message = AUTHENTICATION_EXCEPTION_MESSAGE


class InvalidUserDataException(Exception):
    message = INVALID_USER_DATA_EXCEPTION_MESSAGE


class UserNotFoundException(Exception):
    message = USER_NOT_FOUND_EXCEPTION_MESSAGE
