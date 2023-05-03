UNKNOWN_EXCEPTION_MESSAGE = 'An unknown exception occurred.'
INVALID_TEAM_DATA_EXCEPTION_MESSAGE = "Invalid team data"
TEAM_NOT_FOUND_EXCEPTION_MESSAGE = "Team not found"
EVENT_NOT_FOUND_EXCEPTION_MESSAGE = "Event not found"
USER_IS_NOT_TEAM_LEADER_EXCEPTION_MESSAGE = "User is not team leader"
USER_IS_NOT_TEAM_MEMBER_EXCEPTION_MESSAGE = "User is not team member"
USER_ALREADY_HAS_PARTICIPATION_EXCEPTION_MESSAGE = "User already has participation"
PARTICIPANT_NOT_FOUND_EXCEPTION_MESSAGE = "User is not participant"
INVALID_PARTICIPANT_STATUS_EXCEPTION_MESSAGE = "Invalid participant status"
PARTICIPANT_ALREADY_HAS_STATUS_EXCEPTION_MESSAGE = "Participant already has status"


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


class UserAlreadyHasParticipationException(Exception):
    message = USER_ALREADY_HAS_PARTICIPATION_EXCEPTION_MESSAGE


class ParticipantNotFoundException(Exception):
    message = PARTICIPANT_NOT_FOUND_EXCEPTION_MESSAGE


class InvalidParticipantStatusException(Exception):
    message = INVALID_PARTICIPANT_STATUS_EXCEPTION_MESSAGE


class ParticipantAlreadyHasStatusException(Exception):
    message = PARTICIPANT_ALREADY_HAS_STATUS_EXCEPTION_MESSAGE
