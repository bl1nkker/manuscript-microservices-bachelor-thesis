INVALID_TEAM_DATA_EXCEPTION_MESSAGE = "Invalid team data"
TEAM_NOT_FOUND_EXCEPTION_MESSAGE = "Team not found"
EVENT_NOT_FOUND_EXCEPTION_MESSAGE = "Event not found"
USER_IS_NOT_TEAM_LEADER_EXCEPTION_MESSAGE = "User is not team leader"
USER_IS_NOT_TEAM_MEMBER_EXCEPTION_MESSAGE = "User is not team member"


class InvalidTeamDataException(Exception):
    message = INVALID_TEAM_DATA_EXCEPTION_MESSAGE


class EventNotFoundException(Exception):
    message = EVENT_NOT_FOUND_EXCEPTION_MESSAGE


class TeamNotFoundException(Exception):
    message = TEAM_NOT_FOUND_EXCEPTION_MESSAGE


class UserIsNotTeamLeaderException(Exception):
    message = USER_IS_NOT_TEAM_LEADER_EXCEPTION_MESSAGE


class UserIsNotTeamMemberException(Exception):
    message = USER_IS_NOT_TEAM_MEMBER_EXCEPTION_MESSAGE
