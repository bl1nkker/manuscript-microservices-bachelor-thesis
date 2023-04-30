INVALID_TEAM_DATA_EXCEPTION_MESSAGE = "Invalid team data"
USER_IS_NOT_NOTIFICATION_OWNER_EXCEPTION_MESSAGE = "User is not notification owner"
NOTIFICATION_NOT_FOUND_EXCEPTION_MESSAGE = "Notification not found"


class NotificationNotFoundException(Exception):
    message = NOTIFICATION_NOT_FOUND_EXCEPTION_MESSAGE


class UserIsNotNotificationOwnerException(Exception):
    message = USER_IS_NOT_NOTIFICATION_OWNER_EXCEPTION_MESSAGE
